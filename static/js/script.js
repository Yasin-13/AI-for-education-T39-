// Function to validate the registration form
function validateRegistrationForm() {
    var fullname = document.getElementById('fullname').value;
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;

    if (fullname.trim() == '' || email.trim() == '' || password.trim() == '') {
        alert('Please fill in all fields.');
        return false;
    }

    return true;
}
