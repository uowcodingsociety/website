titleTexts = ["Learn to code.", "Meet other developers.", "Expand your career options.", "Take on meaningful projects.", "Collaborate with entrepreneurs."];

$(function() {
      StartTextAnimation(0);
});

  // type one text in the typwriter
  // keeps calling itself until the text is finished
  function typeWriter(text, i, fnCallback) {
    // chekc if text isn't finished yet
    if (i < (text.length)) {
      // add next character to h1
     $("#title-text").html(text.substring(0, i+1));

      // wait for a while and call this function again for next character
      setTimeout(function() {
        typeWriter(text, i + 1, fnCallback)
      }, Math.random() * (100) + 50);
    }
    // text finished, call callback if there is a callback function
    else if (typeof fnCallback == 'function') {
      // call callback after timeout
      setTimeout(fnCallback, 700);
    }
  }
  // start a typewriter animation for a text in the dataText array
   function StartTextAnimation(i) {
     if (typeof titleTexts[i] == 'undefined'){
        setTimeout(function() {
          StartTextAnimation(0);
        }, 20000);
     }
     // check if dataText[i] exists
    if (i < titleTexts[i].length) {
      // text exists! start typewriter animation
     typeWriter(titleTexts[i], 0, function(){
       // after callback (and whole text has been animated), start next text
       $("#title-text").html("");
       StartTextAnimation((i + 1) % titleTexts.length);
     });
    }
  }