function displayModalContent(data) {
    $("#modal-content").html(data);
    let messages = $("#messages-missinganime")[0];
    if (messages) {
        new Vue({ el: messages });
    }
}

function loadModalData() {
    $.get(
        this.url,
        displayModalContent
    );
}

function sendModalData(event) {
    event.preventDefault();
    let posting = $.post(
        this.url,
        $("#form-missinganime").serialize()
    );
    posting.done(displayModalContent);
}

$(window).on(
    "beforeunload",
    function(e) {
        e.preventDefault();
        // Newer browsers ignore the return value, but certain older browsers display this in the dialog.
        e.returnValue = "Do you want to leave the survey page? Changes you made may not be saved.";
        return "Do you want to leave the survey page? Changes you made may not be saved.";
    }
);
