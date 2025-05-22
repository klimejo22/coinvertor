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

        console.log("localhost:8000/convert/" + currencyValues[0] + "/" + currencyValues[1] + "/" + inputValues[0])

        $.get("/api/convert/" + currencyValues[0] + "/" + currencyValues[1] + "/" + inputValues[0], function (data) {
            
            console.log(data)

            if (data.Result == "success") {

                $("#amountTo").val(Math.round(parseFloat(data.c2_val) * 1000) / 1000);
                $("#amountFrom").val("")

            } else {
                alert("Error 500: " + data.Result)
            }

        })

      } else if (inputValues[0] == "" && inputValues[1] != ""){

        console.log("localhost:8000/convert/" + currencyValues[1] + "/" + currencyValues[0] + "/" + inputValues[1])

        $.get("/api/convert/" + currencyValues[1] + "/" + currencyValues[0] + "/" + inputValues[1], function (data) {
          
          console.log(data)

            if (data.Result == "success") {

                $("#amountFrom").val(Math.round(parseFloat(data.c2_val) * 1000) / 1000);
                $("#amountTo").val("")

            } else {
                alert("Error 500: " + data.Result)
            }
        })
      } else {
        alert("Skibidi spatne")
      }
    });
  });