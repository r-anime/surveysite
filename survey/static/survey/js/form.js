function displayModalContent(data) {
    $("#modal-content").html(data);
    let messages = $("#messages-missinganime");
    if (messages.length) {
        new Vue({el: "#messages-missinganime"});
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
