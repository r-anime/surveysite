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
