const initializeBackButton = () => {
    const backButton = document.getElementById("back-button");

    if (backButton === null)
        return;

    backButton.onmouseover = () => {
        backButton.style.cursor = "pointer";
    };
}

initializeBackButton();
