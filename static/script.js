
const garnitures = document.querySelectorAll(
    ".divRadio input[type='checkbox']"
);

const MAX_GARNITURES = 4;

garnitures.forEach(garniture => {
    garniture.addEventListener("change", function () {

        const selection = document.querySelectorAll(
            ".divRadio input[type='checkbox']:checked"
        );

        if (selection.length > MAX_GARNITURES) {
            this.checked = false;
            alert("Vous ne pouvez choisir que 4 garnitures maximum !");
        }

    });
});
