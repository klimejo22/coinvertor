$(document).ready(function () {

        $.get("/api/lastUpdate", function(data){
            console.log(data)
            $("#update").append(data.Last_Update)
            console.log(Date.now() / 1000)
            if (Date.now() / 1000 >= data.Timestamp) {
                $.get("/api/update", function(data){
                    console.log(data)
                })
            }
        })


})