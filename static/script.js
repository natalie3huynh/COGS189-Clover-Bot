// function expandButton(id) {
//     document.querySelectorAll(".grid-item").forEach(btn => {
//         btn.classList.remove("expanded");
//     });

//     document.getElementById(id).classList.add("expanded");
// }

// document.addEventListener("DOMContentLoaded", function () {
//     document.querySelectorAll(".grid-item").forEach(button => {
//         button.addEventListener("click", function () {
//             expandButton(this.id);
//         });
//     });
// });
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".grid-btn").forEach(button => {
        button.addEventListener("click", () => {
            alert(`Button ${button.textContent} clicked!`);
        });
    });
});

