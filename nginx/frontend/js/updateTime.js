$(document).ready(function () {

        $.get("/api/lastUpdate", function(data){
            console.log(data)
            $("#update").append(data.Last_Update)
        })

})