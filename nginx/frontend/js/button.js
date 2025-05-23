 $(document).ready(function () {

    $('#convert').on('click', function () {

      const inputValues = [
        $('#amountFrom').val().trim(),
        $('#amountTo').val().trim()
      ];

      const currencyValues = [
        $('#currencyFrom').val().trim(),
        $('#currencyTo').val().trim()
      ];

      console.log("Input hodnoty:", inputValues);
      console.log("Vybrané měny:", currencyValues);
      console.log(inputValues[0] != "" && inputValues[1] == "")

      if (inputValues[0] != "" && inputValues[1] == "") {

        convert(currencyValues[0], currencyValues[1], inputValues[0], "#amountTo", "#amountFrom")

      } else if (inputValues[0] == "" && inputValues[1] != ""){

        convert(currencyValues[1], currencyValues[0], inputValues[1], "#amountFrom", "#amountTo")

      } else {

        alert("Skibidi spatne")
        
      }

    });

  });