$(document).ready(function () {
    $(".slider").on("input", function () {
        let vital = $(this).attr("id");
        let value = $(this).val();

        $("#" + vital + "_value").text(value);

        $.ajax({
            url: "/update_vital",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ "vital": vital, "value": value }),
            success: function (response) {
                if (response.status === "success") {
                    $("#" + vital + "_change").text(response.updated_data[vital].change);
                }
            }
        });
    });
});
