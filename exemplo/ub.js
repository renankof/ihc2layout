// le cookie
function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

$(document).ready(function() {
  // get id session
  var sessionId;
  $.get( "http://www.carroquente.com.br:5000/getSessionId", function(data){
    sessionId = data.sessionId;
  }, "json");
  // verifica se o usuário é conhecido
  var user = readCookie('UB-User-Identification');
  if (user == null){
      // cookie não existe, entao cria identificador
      $.get( "http://www.carroquente.com.br:5000/createIdentUser", function(data){
        //$.cookie('UB-User-Identification' , data.identUser);
        document.cookie = "UB-User-Identification="+data.identUser;
        user = data.identUser;
      }, "json");
      // pega o valor do cookie

  }
  var rWidth = screen.width;
  var rHeight =  screen.height;
  // vars de análise
  var countA = 0;
  var countB = 0;
  var clickA = 0;
  var clickB = 0;
  var timeA = 0;
  var timeB = 0;
  var intervalSample = 5;
  var sessionTime = $.now();
  // var aux
  var tempTime = 0;
  // classe tipo A
  $( ".typeA" ).hover(
    function() {
      tempTime = $.now();
      countA += 1;
    }, function() {
      timeA +=  $.now() - tempTime;
    }
  );
  // classe tipo B
  $( ".typeB" ).hover(
    function() {
      tempTime = $.now();
      countB += 1;
    }, function() {
      timeB += $.now() - tempTime;
    }
  );
  // count click classe A
  $( ".typeA" ).click(
    function() {
      clickA +=1;
    }
  );
  // count click classe B
  $( ".typeB" ).click(
    function() {
      clickB +=1;
    }
  );
  // envia informações via api
  $( ".send" ).click(function() {
    $.get( "http://www.carroquente.com.br:5000/getData",
                      {
                        rWidth: rWidth,
                        rHeight: rHeight,
                        countA: countA,
                        countB: countB,
                        clickA: clickA,
                        clickB: clickB,
                        timeA: timeA,
                        timeB: timeB,
                        intervalSample: intervalSample,
                        sessionTime: $.now() - sessionTime,
                        sessionId: sessionId,
                        user: user
                      });
  });

  setInterval(function() {
          $.get( "http://www.carroquente.com.br:5000/getData",
                            {
                              rWidth: rWidth,
                              rHeight: rHeight,
                              countA: countA,
                              countB: countB,
                              clickA: clickA,
                              clickB: clickB,
                              timeA: timeA,
                              timeB: timeB,
                              intervalSample: intervalSample,
                              sessionTime: $.now() - sessionTime,
                              sessionId: sessionId,
                              user: user
                            });
        }, 30*1000);
});
