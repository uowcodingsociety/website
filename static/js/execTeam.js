function deselect(e) {
  e.removeClass('selected');
  $('.pop').slideFadeToggle(function() {});
}

$.fn.slideFadeToggle = function(easing, callback) {
  return this.animate({ opacity: 'toggle'}, 'fast', easing, callback);
};

function showExecPopUp(name, course, bio, nationality, pronouns, team, title, imageName, liLink, year, ghLink=""){
    selected = false;
    var scrollPos = document.documentElement.scrollTop;
    console.log(scrollPos);
    $(".personButton").each(function() {
        if($(this).hasClass("selected")){
            deselect($(this));
            selected = true;
        }
    });
    if(!selected){
        $("#execPopUp").css("top", scrollPos + $(window).height() / 2 - $("#execPopUp").height() / 2);
        $("#execPopName").html(name);
        $("#execPopTitle").html(title);
        $("#execPopNationality").html(nationality);
        $("#execPopCourse").html(course);
        $("#execPopYear").html(year);
        $("#execPopBio").html(bio);
        $("#execPopImage").attr("src", "/static/assets/exec-images/" + imageName + ".png");
        $(".personButton").first().addClass("selected");
        $(".pop").slideFadeToggle();
    }

}