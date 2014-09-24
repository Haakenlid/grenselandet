$(function() {
  $('.card-number').keyup(function() {
    var detector = new BrandDetection();
    var cc_number = $('.card-number').val().replace(/\D/g, '')
    var brand = detector.detect(cc_number);
    $(".card-number")[0].className = "card-number";
    if (brand !== 'unknown') {
      $('.card-number').addClass("paymill-card-number-" + brand);
    }
    if (!detector.validate(cc_number)) {
      $('.card-number').addClass("paymill-card-number-grayscale");
    }
    if (brand !== 'maestro') {
      VALIDATE_CVC = true;
    } else {
      VALIDATE_CVC = false;
    }
  });

  $('.card-expiry').keyup(function() {
      if ( /^\d\d$/.test( $('.card-expiry').val() ) ) {
          text = $('.card-expiry').val();
          $('.card-expiry').val(text += "/");
      }
  });

  $('#payment-form').submit(function (event) {

    $('.submit-button').attr("disabled", "disabled");

    var expiry = $('.card-expiry').val();
    expiry = expiry.split("/");

    var params = {
      amount_int:     parseInt($('.card-amount').val().replace(/[\.,]/, '.') * 100),
      currency:       $('.card-currency').val(),
      number:         $('.card-number').val().replace(/\D/,''),
      exp_month:      expiry[0],
      exp_year:       expiry[1],
      cvc:            $('.card-cvc').val(),
      cardholder:     $('.card-holdername').val()
    };

    paymill.createToken(params, PaymillResponseHandler);
    return false;
  });

  function PaymillResponseHandler(error, result) {
    if (error) {
      switch (error.apierror){
        case 'field_invalid_card_number':
          InputError('.card-number', 'This card number seems to be invalid.');
          break;

        case 'field_invalid_card_exp':
          InputError('.card-expiry', 'This expiration date seems to be invalid.');
          break;

        case 'field_invalid_card_cvc':
          InputError('.card-cvc', 'This verficiation code seems to be invalid.');
          break;

        case 'field_invalid_card_holder':
          InputError('.card-holdername', 'The name of the credit card holder seems to be invalid.');
          break;

        default:
          alert('error in credit card details.')
          break;
      }
    } else {
      var form = $("#payment-form");
      var token = result.token;
      form.append("<input type='hidden' name='paymill_token' value='" + token + "'/>");
      form.get(0).submit();
    }
    $(".submit-button").removeAttr("disabled");
  }

  function InputError(inputclass, message) {
    input = $(inputclass)[0];
    input.setCustomValidity(message);
    input.oninput = function(){
      this.setCustomValidity('');
    }
    $(".submit-button").removeAttr("disabled");
    $(".submit-button").click();

    // input.setCustomValidity('');
    // document.getElementById("payment-form").submit();
  }
});