$(function () {
    setIndexColours();
})

/* This is a hack for categorising google calendar event types based on their names.
Required as google calendar does not contain this functionality within the same calendar */

var coursesColour = "#008EFF"
var socialsColour = "#EB8ED6"
var otherColour = "#D8BDA6"
var careersColour = "#85D08E"

function parseEventTypes() {
    $(".fc-event-title").each(function(index, element) {
        var eventTitle = $(element).html();
        var eventTextSplit = eventTitle.split("@")
        if(eventTextSplit.length == 2) {
            var eventType = eventTextSplit[0].trim();
            var eventTitle = eventTextSplit[1].trim();
            switch(eventType){
                case "courses":
                    $(element).parent().css("background-color", coursesColour)
                    break;
                case "social":
                    $(element).parent().css("background-color", socialsColour)
                    break;
                case "other":
                    $(element).parent().css("background-color", otherColour)
                    break;
                case "careers":
                    $(element).parent().css("background-color", careersColour)
                    break;
            }
            $(element).html(eventTitle)

        }
    })

    $(".fc-list-event-title a").each(function(index, element) {
        var eventTitle = $(element).html();
        var eventTextSplit = eventTitle.split("@")
        if(eventTextSplit.length == 2) {
            var eventType = eventTextSplit[0].trim();
            var eventTitle = eventTextSplit[1].trim();
            switch(eventType){
                case "courses":
                    // $(element).parent().css("background-color", coursesColour)
                    $(element).css("background-color", coursesColour)
                    break;
                case "social":
                    $(element).css("background-color", socialsColour)
                    break;
                case "other":
                    $(element).css("background-color", otherColour)
                    break;
                case "careers":
                    $(element).css("background-color", careersColour)
                    break;
                default:
                    console.log("Event type not found: " + eventType);
            }
            $(element).html(eventTitle)

        }
    })
}

function setIndexColours() {
    $("#coursesColourSquare").css("background-color", coursesColour)
    $("#socialColourSquare").css("background-color", socialsColour)
    $("#otherColourSquare").css("background-color", otherColour)
    $("#careersColourSquare").css("background-color", careersColour)
}

  var calendar;
  document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendarType = (window.innerWidth <= 1060) ? "listWeek" : "dayGridMonth";
    calendar = new FullCalendar.Calendar(calendarEl, {
    loading: function(loading) {
        if(!loading){
            setTimeout(function() { parseEventTypes(); }, 1);
        }
    },
    initialView: calendarType,
    googleCalendarApiKey: 'AIzaSyCzbQq8jTFGVnOQxqqt3RGdxulJ-Cl12t8',
    events: {
      googleCalendarId: 'kim8h0qrkcsocf683vjuagremg@group.calendar.google.com'
    },
    eventTimeFormat: {
      hour: 'numeric',
      minute: '2-digit',
      meridiem: 'short'
    },
    });
    calendar.render();
  });

  window.addEventListener('resize', function(event){
    var newWidth = window.innerWidth;
    if(newWidth < 1060){
      console.log(calendar.view.type);
      if(calendar.view.type == "dayGridMonth"){
        calendar.changeView("listWeek");
        parseEventTypes();
      }
    } else {
      if(calendar.view.type == "listWeek"){
        calendar.changeView("dayGridMonth");
        parseEventTypes();
      }
    }
  });