var baseUrl = "/api/convert?"
function convert(c1, c2, val, id1, id2) {
    var url = baseUrl + "c1="+ c1 + "&c2=" + c2 + "&val=" + val
    console.log(url)
    $.get(url, function (data) {
       console.log(data)

        if (data.Result == "success") {

            $(id1).val(Math.round(parseFloat(data.c2_val) * 1000) / 1000);
            $(id2).val("")

        } else {
            alert("Error 500: " + data.Result)
        } 

    })
}