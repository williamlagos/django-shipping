#!/usr/bin/python
#
# This file is part of django-ship project.
#
# Copyright (C) 2011-2020 William Oliveira de Lagos <william.lagos@icloud.com>
#
# Shipping is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shipping is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Shipping. If not, see <http://www.gnu.org/licenses/>.
#

import urllib
import http
import re

from xml.dom import minidom
from bs4 import BeautifulStoneSoup as BSS
# from .beautifulsoup import BeautifulSoup

FORMATOS = {
    'PACOTE': 1,
    'ROLO': 2,
}

SERVICOS = {
    'PAC':'41106',
    'SEDEX':'40010',
    'SEDEX10':'40215',
    'SEDEXHOJE':'40290',
    'SEDEXCOBRAR':'40045',
    'ALL': '41106,40010,40215,40290,40045',
}

URL_CORREIOS = 'http://www.buscacep.correios.com.br/servicos/dnec/'

class EncomendaRepository(object):
        
    def __init__(self):
        from scraping import CorreiosWebsiteScraper
        self.correios_website_scraper = CorreiosWebsiteScraper()
    
    def get(self, numero):
        return self.correios_website_scraper.get_encomenda_info(numero)

class Encomenda(object):
    
    def __init__(self, numero):
        self.numero = numero
        self.status = []
    
    def adicionar_status(self, status):
        self.status.append(status)
        self.status.sort(lambda x, y: 1 if x.data > y.data else -1)
    
    def ultimo_status_disponivel(self):
        return self.status[len(self.status) - 1] if len(self.status) > 0 else None

    def primeiro_status_disponivel(self):
        return self.status[0] if len(self.status) > 0 else None

class Status(object):
    
    def __init__(self, **kwargs):
        self.data = kwargs.get('data')
        self.local = kwargs.get('local')
        self.situacao = kwargs.get('situacao')
        self.detalhes = kwargs.get('detalhes')

class Correios:
    def __init__(self): pass

class CorreiosWebsiteScraper(object):
    
    def __init__(self, http_client=urllib2):
        self.url = 'http://websro.correios.com.br/sro_bin/txect01$.QueryList?P_ITEMCODE=&P_LINGUA=001&P_TESTE=&P_TIPO=001&P_COD_UNI='
        self.http_client = http_client
        
    def get_encomenda_info(self, numero):
        request = self.http_client.urlopen('%s%s' % (self.url, numero))
        html = request.read()
        request.close()
        if html:
            encomenda = Encomenda(numero)
            [encomenda.adicionar_status(status) for status in self._get_all_status_from_html(html)]
            return encomenda
    
    def _get_all_status_from_html(self, html):
        html_info = re.search('.*(<table.*</TABLE>).*', html, re.S)
	try:
	        table = html_info.group(1)
	except AttributeError as e:
		return [-1]
        
        soup = BeautifulSoup(table)
        
        status = []
        count = 0
        for tr in soup.table:
            if count > 4 and str(tr).strip() != '':
                if re.match(r'\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}', tr.contents[0].string):
                    status.append(
                            Status(data=str(tr.contents[0].string),
                                    local=str(tr.contents[1].string),
                                    situacao=str(tr.contents[2].font.string))
                    )
                else:
                    status[len(status) - 1].detalhes = str(tr.contents[0].string)
                    
            count = count + 1
        
        return status


class CorreiosCode():
    def __init__(self, proxy=None):
        cj = http.cookiejar.LWPCookieJar()
        cookie_handler = urllib.request.HTTPCookieProcessor(cj)
        if proxy:
            proxy_handler = urllib.request.ProxyHandler({'http': proxy})
            opener = urllib.request.build_opener(proxy_handler, cookie_handler)
        else:
            opener = urllib.request.build_opener(cookie_handler)
        urllib.request.install_opener(opener)

    def _url_open(self, url, data=None, headers=None):
        if headers == None:
            headers = {}

        headers['User-agent'] = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        encoded_data = urllib.parse.urlencode(data) if data else None
        url = URL_CORREIOS + url

        req = urllib.request.Request(url, encoded_data, headers)
        handle = urllib.request.urlopen(req)

        return handle

    def _parse_detalhe(self, html):
        soup = BeautifulSoup(html.decode('ISO-8859-1'))

        value_cells = soup.findAll('td', attrs={'class': 'value'})
        values = [cell.firstText(text=True) for cell in value_cells]
        localidade, uf = values[2].split('/')
        values_dict = {
            'Logradouro': values[0],
            'Bairro': values[1],
            'Localidade': localidade,
            'UF': uf,
            'CEP': values[3]
        }
        return values_dict

    def _parse_linha_tabela(self, tr):
        values = [cell.firstText(text=True) for cell in tr.findAll('td')]
        keys = ['Logradouro', 'Bairro', 'Localidade', 'UF', 'CEP']
        return dict(list(zip(keys, values)))

    def _parse_tabela(self, html):
        soup = BeautifulSoup(html)
        linhas = soup.findAll('tr', attrs={
            'onclick': re.compile(r"javascript:detalharCep\('\d+','\d+'\);")
        })
        return [self._parse_linha_tabela(linha) for linha in linhas]

    def _parse_faixa(self, html):
        if "não está cadastrada" in html.decode('cp1252'):
            return None
        ceps = re.findall('\d{5}-\d{3}', html)
        if len(ceps) == 4 or len(ceps) == 6: #uf (+ uf) + cidade com range
            return tuple(ceps[-2:])
        elif len(ceps) == 3 or len(ceps) == 5: #uf (+ uf) + cidade com cep único
            return ceps[-1]
        else:
            raise ValueError("HTML recebido não é válido")

    def detalhe(self, posicao=0):
        """Retorna o detalhe de um CEP da última lista de resultados"""
        handle = self._url_open('detalheCEPAction.do', {'Metodo': 'detalhe',
                                                        'TipoCep': 2,
                                                        'Posicao': posicao + 1,
                                                        'CEP': ''})
        html = handle.read()
        return self._parse_detalhe(html)

    def consulta_faixa(self, localidade, uf):
        """Consulta site e retorna faixa para localidade"""
        url = 'consultaFaixaCepAction.do'
        data = {
            'UF': uf,
            'Localidade': localidade.encode('cp1252'),
            'cfm': '1',
            'Metodo': 'listaFaixaCEP',
            'TipoConsulta': 'faixaCep',
            'StartRow': '1',
            'EndRow': '10',
        }
        html = self._url_open(url, data).read()
        return self._parse_faixa(html)

    def _correiosurl(self,endereco,uf=None,localidade=None,tipo=None,numero=None):
        if uf is None:
            url = 'consultaEnderecoAction.do'
            data = {
                'relaxation': endereco.encode('ISO-8859-1'),
                'TipoCep': 'ALL',
                'semelhante': 'N',
                'cfm': 1,
                'Metodo': 'listaLogradouro',
                'TipoConsulta': 'relaxation',
                'StartRow': '1',
                'EndRow': '10'
            }
        else:
            url = 'consultaLogradouroAction.do'
            data = {
                'Logradouro': endereco.encode('ISO-8859-1'),
                'UF': uf,
                'TIPO': tipo,
                'Localidade': localidade.encode('ISO-8859-1'),
                'Numero': numero,
                'cfm': 1,
                'Metodo': 'listaLogradouro',
                'TipoConsulta': 'logradouro',
                'StartRow': '1',
                'EndRow': '10'
            }
        return self._parse_tabela(self._url_open(url, data).read())[0]


    def _rvirtualurl(self,cep):
        url = 'http://cep.republicavirtual.com.br/web_cep.php?formato=' \
              'xml&cep=%s' % str(cep)
        dom = minidom.parse(urllib.request.urlopen(url))

        tags_name = ('uf',
                     'cidade',
                     'bairro',
                     'tipo_logradouro',
                     'logradouro',)

        resultado = dom.getElementsByTagName('resultado')[0]
        resultado = int(resultado.childNodes[0].data)
        if resultado != 0:
            return self._getdata(tags_name, dom)
        else:
            return {}

    def _getdata(self, tags_name, dom):
        dados = {}

        for tag_name in tags_name:
            try:
                dados[tag_name] = dom.getElementsByTagName(tag_name)[0]
                dados[tag_name] = dados[tag_name].childNodes[0].data
            except:
                dados[tag_name] = ''

        return dados

    def consulta(self, cep, correios=False, uf=None, localidade=None, tipo=None, numero=None):
        """Consulta site e retorna lista de resultados"""
        if correios:
            return self._correiosurl(cep,uf,localidade,tipo,numero)
        else:
            return self._rvirtualurl(cep)


class CorreiosShippingService(object):
    def __init__(self, cep_origem='80050370'):
        #ceps
        self.cep_origem = cep_origem
        self.cep_destino = None
        
        #servicos
        self.aviso_recebimento = 'N'
        self.valor_declarado = 0
        self.mao_propria = 'N'
        self.servico = 'ALL'

        #medidas
        self.formato = 'PACOTE'
        self.altura = 0
        self.largura = 0
        self.comprimento = 0
        self.diametro = 0
        self.peso = 0.3

        #configs
        self.empresa = '' #id da empresa, quando possui contrato
        self.senha = ''   #senha
        self.tipo = 'xml'
        self.URL = 'http://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx'
        
        self.response = None
        self.hash = {}
        self.results = {}
        self.errors = {}

    def __call__(self, cep_destino=None, servico=None,):
        """
        Call :)
        """
        if cep_destino:
            self.cep_destino = cep_destino

        # pega o codigo do servico p/ envio ao webservice
        if servico and servico in SERVICOS:
            self.servico = servico
        
        # valida medidas e pesos minimos
        self._validate()

        # prepara o hash para envio
        self._build_hash()

        # envia os parametros e recupera o retorno
        self._request()

        # processa o resultado
        self._parse()


    def _build_hash(self):
        """
        Cria hash com dados instanciados
        """
        h = self.hash
        h['nCdEmpresa'] = self.empresa
        h['sDsSenha'] = self.senha
        h['strRetorno'] = self.tipo
        h['sCdMaoPropria'] = self.mao_propria
        h['nVlValorDeclarado'] = self.valor_declarado
        h['sCdAvisoRecebimento'] = self.aviso_recebimento
        h['nCdFormato'] = FORMATOS[self.formato]
        h['sCepOrigem'] = self.cep_origem
        h['sCepDestino'] = self.cep_destino
        h['nCdServico'] = SERVICOS[self.servico]
        h['nVlAltura'] = self.altura
        h['nVlLargura'] = self.largura
        h['nVlComprimento'] = self.comprimento
        h['nVlDiametro'] = self.diametro
        h['nVlPeso'] = self.peso
        self.hash = h


    def _validate(self):
        """ Valida as medidas (apenas os minimos)
        para calculo
        """

        peso_minimo = 0.3
        if self.formato == 'ROLO':
            comprimento_minimo = 18
            diametro_minimo = 5
            altura_minima = 0
            largura_minima = 0
        else:
            comprimento_minimo = 16
            diametro_minimo = 0
            altura_minima = 2
            largura_minima = 5

        if self.diametro < diametro_minimo:
            self.diametro = diametro_minimo

        if self.altura < altura_minima:
            self.altura = altura_minima

        if self.comprimento < comprimento_minimo:
            self.comprimento = comprimento_minimo

        # altura nao pode ser maior que comprimento
        if self.altura > self.comprimento:
            self.altura = self.comprimento

        if self.largura < largura_minima:
            self.largura = largura_minima

        # largura nao pode ser menor que 11cm quando o comprimento
        # for menor que 25cm (apenas no formato PACOTE)
        if self.formato == 'PACOTE' and self.largura < 11 \
            and self.comprimento < 25:
            self.largura = 11

        if self.peso < peso_minimo:
            self.peso = peso_minimo


    def _request(self):
        """ 
        Realiza a requisicao ao webservice e recupera
        o retorno
        """
        url = '%s?%s' %(self.URL, urllib.parse.urlencode(self.hash))
        self.response = urllib.request.urlopen(url).read()


    def _parse(self):
        """
        Processa o xml retornado pelo webservice
        utilizando o BeautifulSoup

        Exemplo do retorno:
            <cServico>
                <Codigo>40045</Codigo>
                <Valor>12,10</Valor>
                <PrazoEntrega>1</PrazoEntrega>
                <ValorMaoPropria>0,00</ValorMaoPropria>
                <ValorAvisoRecebimento>0,00</ValorAvisoRecebimento>
                <ValorValorDeclarado>1,00</ValorValorDeclarado>
                <EntregaDomiciliar>S</EntregaDomiciliar>
                <EntregaSabado>S</EntregaSabado>
                <Erro>0</Erro>
                <MsgErro></MsgErro>
            </cServico>
        """
        self.xmltree = BSS(self.response, selfClosingTags=[],
                    convertEntities=BSS.ALL_ENTITIES)

        for result in self.xmltree('cservico'):
            servico_id = result('codigo')[0].contents[0]
            prazo = result('prazoentrega')[0].contents[0]
            valor = result('valor')[0].contents[0]
            erro = result('erro')[0].contents[0]
            servico = [k for k in SERVICOS if SERVICOS[k] == servico_id][0]

            #outras opcoes disponiveis no retorno:
            #valor_mao_propria = result('valormaopropria')[0].contents[0]
            #valor_aviso_recebimento = result('valoravisorecebimento')[0].contents[0]
            #valor_valor_declarado = result('valorvalordeclarado')[0].contents[0]
                        
            if erro != '0':
                msgerro = result('msgerro')[0].contents[0]
                self.errors[servico] = msgerro
            else:
                self.results[servico] = prazo, valor


    def print_results(self):
        """
        Imprime o resultado no terminal
        """
        if self.results:
            print('Resultados:')
            for k, v in self.results.items():
                prazo, valor = v
                print('%s - %s dias - R$ %s' %(k, prazo, valor))
        
        if self.errors:
            print('Erros:')
            for k, v in self.errors.items():
                print('%s - %s' %(k, v))
