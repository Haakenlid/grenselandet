// jQuery(document).ready(function ($) {

function logResponse(res) {
  // create console.log to avoid errors in old IE browsers
  if (!window.console) console = {log:function(){}};
  console.log(res);

  if(PAYMILL_TEST_MODE)
    $('.debug').text(res).show().fadeOut(3000);
}

  // function PaymillResponseHandler(error, result) {
  //   if (error) {
  //     // Shows the error above the form
  //     $(".payment-errors").text(error.apierror);
  //     $(".submit-button").removeAttr("disabled");
  //   } else {
  //     var form = $("#payment-form");
  //     // Output token
  //     var token = result.token;
  //     // Insert token into form in order to submit to server
  //     // form.append(token);
  //     $(".payment-errors").text(token);
  //   }
  // }
       // var doc = document;
       // var body = $( doc.body );

$('.card-number').keyup(function() {
 var detector = new BrandDetection();
 var brand = detector.detect($('.card-number').val());
 $(".card-number")[0].className = $(".card-number")[0].className.replace(/paymill-card-number-.*/g, '');
 if (brand !== 'unknown') {
   $('.card-number').addClass("paymill-card-number-" + brand);

   if (!detector.validate($('.card-number').val())) {
     $('.card-number').addClass("paymill-card-number-grayscale");
   }

   if (brand !== 'maestro') {
     VALIDATE_CVC = true;
   } else {
     VALIDATE_CVC = false;
   }
 }
});

$('.card-expiry').keyup(function() {
 if ( /^\d\d$/.test( $('.card-expiry').val() ) ) {
   text = $('.card-expiry').val();
   $('.card-expiry').val(text += "/");
 }
});


function PaymillResponseHandler(error, result) {
 if (error) {
   $(".payment_errors").css("display","inline-block");
   $(".payment_errors").text(error.apierror);
 } else {
   $(".payment_errors").css("display","none");
   $(".payment_errors").text("");
   var form = $("#payment-form");
       // Token
       var token = result.token;
       form.append("<input type='hidden' name='paymill_token' value='" + token + "'/>");
       form.get(0).submit();
     }
    $(".submit-button").removeAttr("disabled");
  }

$("#payment-form").submit(function (event) {

  $('.submit-button').attr("disabled", "disabled");

  if (false === paymill.validateHolder($('.card-holdername').val())) {
    $(".payment_errors").text("invalid-card-holdername");
    $(".payment_errors").css("display","inline-block");
    $(".submit-button").removeAttr("disabled");
    return false;
  }

  if ((false === paymill.validateCvc($('.card-cvc').val()))) {
    if(VALIDATE_CVC){
      $(".payment_errors").text("invalid-card-cvc");
      $(".payment_errors").css("display","inline-block");
      $(".submit-button").removeAttr("disabled");
      return false;
    } else {
      $('.card-cvc').val("000");
    }
  }

  if (false === paymill.validateCardNumber($('.card-number').val())) {
    $(".payment_errors").text("invalid-card-number");
    $(".payment_errors").css("display","inline-block");
    $(".submit-button").removeAttr("disabled");
    return false;
  }

   // var expiry = $('.card-expiry').val();
   // expiry = expiry.split("/");
   // if(expiry[1] && (expiry[1].length <= 2)){
   //   expiry[1] = '20'+expiry[1];
   // }
   // if (false === paymill.validateExpiry(expiry[0], expiry[1])) {
   //   $(".payment_errors").text("invalid-card-expiry-date");
   //   $(".payment_errors").css("display","inline-block");
   //   $(".submit-button").removeAttr("disabled");
   //   return false;
   // }

  var params = {
    amount_int:     parseInt($('.card-amount').val().replace(/[\.,]/, '.') * 100),  // E.g. "15" for 0.15 Eur
    currency:       $('.card-currency').val(),    // ISO 4217 e.g. "EUR"
    number:         $('.card-number').val(),
    exp_month:      $('.card-expiry-month').val(),
    exp_year:       $('.card-expiry-year').val(),
    cvc:            $('.card-cvc').val(),
    cardholder:     $('.card-holdername').val()
  };

  paymill.createToken(params, PaymillResponseHandler);
  return false;
});
