$("#visualization-form").on("submit", function(event) {
    event.preventDefault();
    const payload = {
        query: $("#query").val(),
        chart_type: $("#chart_type").val(),
        // ... other parameters ...
    };
    
    $.ajax({
        url: "/plot",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify(payload),
        success: function(response) {
            // Handle the successful response
        },
        error: function(error) {
            // Handle errors
        }
    });
});
