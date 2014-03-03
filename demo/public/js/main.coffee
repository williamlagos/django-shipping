document.documentElement.style.overflowX = "hidden"
#document.documentElement.style.overflowY = 'hidden';

$(document).ready ->
  $.ajaxSetup cache: false
  $("input:submit, button", "#botoes").button()
  $.fn.eventLoop()