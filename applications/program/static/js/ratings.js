$(document).ready(function() {
  myRatings = $('div.rating');
  $.each(myRatings, function(){
    var myCell = this;
    var starContainer = $("div.starcontainer", this);
    var dataSpan = $("span.data", this);
    var values = dataSpan.text().match(/\d+/g);
    if (values.length == 3) {
      var priority = parseInt(values[0]);
      var signup_pk = parseInt(values[1]);
      var multistar = parseInt(values[2]);
      var callback = function(data){
        setTimeout( function(){
          $("div", starContainer).removeClass(
            'jquery-ratings-spin').hide( 1,
            function(){$(this).show()});
          }, 1000);
      }

      var changeRating = function(event, data){
        dataSpan.text(data.rating);
        $("div", starContainer).addClass('jquery-ratings-spin')
        Dajaxice.applications.program.change_rating(callback,
          {'signup_pk':signup_pk,
          'newrating':data.rating})
        $("table.info").trigger("update");

      }
      $(starContainer).ratings(multistar, priority).bind(
        'ratingchanged', changeRating);
    };
  });
});


jQuery.fn.ratings = function(stars, firstRating) {

  //Save  the jQuery object for later use.
  var elements = this;

  //Go through each object in the selector and create a ratings control.
  return this.each(function() {

    //Make sure intialRating is set.
    var initialRating = firstRating ? firstRating : 0

    //Save the current element for later use.
    var containerElement = this;

    //grab the jQuery object for the current container div
    var container = jQuery(this);

    //Create an array of stars so they can be referenced again.
    var starsCollection = Array();

    //Save the initial rating.
    containerElement.rating = initialRating;


    //create each star
    for(var starIdx = 0; starIdx < stars; starIdx++) {


      var newTitles = function(){
        rating = containerElement.rating;
        if (rating == 0 && starsCollection.length==1){
          starsCollection[0].prop('title','I want to attend this')
        } else if (rating == 1){
          starsCollection[0].prop('title','Click to cancel signup')
        } else {
          starsCollection[0].prop('title','I might want to attend this')
        }
        if (starsCollection[1]){
          starsCollection[1].prop('title','I want to attend this')
        }
        if (starsCollection[2]){
          starsCollection[2].prop('title','I really want to attend this!')
        }
        if (starsCollection[3]){
          starsCollection[3].prop('title','I really, really want to attend this!')
        }
      }

      //Create a div to hold the star.
      var starElement = document.createElement('div');

      //Get a jQuery object for this star.
      var star = jQuery(starElement);

      //Store the rating that represents this star.
      starElement.rating = starIdx + 1;

      //Add the style.
      star.addClass('jquery-ratings-star');


      //Add the full css class if the star is beneath the initial rating.
      if(starIdx < initialRating) {
        star.addClass('jquery-ratings-full');
      }

      //add the star to the container
      container.append(star);
      starsCollection.push(star);

      if (registration_closed == false){
        newTitles();

        //hook up the click event
        star.click(function() {
          //When clicked, fire the 'ratingchanged' event handler.  Pass the rating through as the data argument.
          var newRating = (this.rating==1 && containerElement.rating==1)? 0 : this.rating

          elements.triggerHandler("ratingchanged", {rating: newRating});
          containerElement.rating = newRating;
          newTitles();
          if (newRating == 0 && starsCollection.length > 1){
            starsCollection[0].removeClass('jquery-hover-full');
              //starsCollection[0].removeClass('jquery-ratings-full');
            } else if (newRating == 1){
              //starsCollection[0].addClass('jquery-hover-full');
            }

          });

        star.mouseenter(function() {
          //Highlight selected stars.
          if (this.rating == 1 && containerElement.rating == 1 && starsCollection.length > 1){
            myRating = 0;
            starsCollection[0].addClass('jquery-hover-null');
          } else {
            myRating = this.rating;
          }

          for(var index = 0; index < myRating; index++) {
            starsCollection[index].addClass('jquery-hover-full');
          }
          //Unhighlight unselected stars.
          for(var index = myRating; index < stars; index++) {
            starsCollection[index].removeClass('jquery-hover-full');
            starsCollection[index].removeClass('jquery-ratings-full');
          }
        });

        star.mouseleave(function() {
          //Unhighlight selected stars.
          for(var index = 0; index < containerElement.rating; index++) {
            starsCollection[index].addClass('jquery-ratings-full');
            starsCollection[index].removeClass('jquery-hover-full');
            starsCollection[index].removeClass('jquery-hover-null');
          }
          //Unhighlight unselected stars.
          for(var index = containerElement.rating; index < stars ; index++) {
            starsCollection[index].removeClass('jquery-ratings-full');
            starsCollection[index].removeClass('jquery-hover-full');
            starsCollection[index].removeClass('jquery-hover-null');
          }
        });
      }
    }
  });
};
