$(function() {
  $('.card-number').keyup(function() {
    var detector = new BrandDetection();
    var brand = detector.detect($('.card-number').val());
    $(".card-number")[0].className = $(".card-number")[0].className.replace(/paymill-card-number-.*/g, '');
    if (brand !== 'unknown') {
      $('.card-number').addClass("paymill-card-number-" + brand);
    }
    if (!detector.validate($('.card-number').val())) {
      $('.card-number').addClass("paymill-card-number-grayscale");
    }
    if (brand !== 'maestro') {
      VALIDATE_CVC = true;
    } else {
      VALIDATE_CVC = false;
    }
  });

  $('#payment-form').submit(function (event) {
    $('.submit-button').attr("disabled", "disabled");

    // if (false === paymill.validateHolder($('.card-holdername').val())) {
    //   $(".payment_errors").text("invalid-card-holdername");
    //   $(".payment_errors").css("display","inline-block");
    //   $(".submit-button").removeAttr("disabled");
    //   return false;
    // }

    // if (false === paymill.validateCvc($('.card-cvc').val())) {
    //   if(VALIDATE_CVC){
    //     $(".payment_errors").text("invalid-card-cvc");
    //     $(".payment_errors").css("display","inline-block");
    //     $(".submit-button").removeAttr("disabled");
    //     return false;
    //   } else {
    //     $('.card-cvc').val("000");
    //   }
    // }

    // if (false === paymill.validateCardNumber($('.card-number').val())) {
    //   // $(".payment_errors").text("invalid-card-number");
    //   $('.card-number').setCustomValidity('invalid card number')
    //   $(".submit-button").removeAttr("disabled");
    //   return false;
    // }

    // var expiry_month = $('.card-expiry-month').val();
    // var expiry_year = $('.card-expiry-year').val();
    // if (expiry_year && (exp_year.length <= 2)){
    //   expiry_year = '20' + expiry_year;
    // }
    // if (false === paymill.validateExpiry(expiry_month, expiry_year)) {
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

  function PaymillResponseHandler(error, result) {
    if (error) {
      switch (error.apierror){
        case 'field_invalid_card_number':
          InputError('.card-number', 'This card number seems to be invalid.');
          break;

        case 'field_invalid_card_exp':
          InputError('.card-expiry-month', 'This expiration date or year seems to be invalid.');
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
      this.setCustomValidity('')
    }
    $(".submit-button").removeAttr("disabled");
    document.getElementById("payment-button").click()

    // input.setCustomValidity('');
    // document.getElementById("payment-form").submit();
  }
});