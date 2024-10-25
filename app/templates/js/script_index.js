"use strict";

document.getElementById('date').addEventListener('input', function (event) {
    let value = event.target.value;

    // Supprimer tout ce qui n'est pas un chiffre
    value = value.replace(/\D/g, '');

    // Ajouter des séparateurs (/) en fonction de la longueur du texte
    if (value.length > 2) {
        value = value.slice(0, 2) + '/' + value.slice(2);
    }
    if (value.length > 5) {
        value = value.slice(0, 5) + '/' + value.slice(5);
    }

    // Mettre à jour la valeur du champ
    event.target.value = value;
});

document.getElementById('searchForm').addEventListener('submit', function (event) {
    event.preventDefault(); // Empêche le formulaire de se soumettre normalement

    // Récupérer les valeurs des champs du formulaire
    const shiptype = document.getElementById('shiptype-select').value;
    let date = document.getElementById('date').value;

    if (date.length === 0) {
        date_format = new Date();
        let jour = date_format.getDate();
        let month = date_format.getMonth() + 1;
        if (jour < 10) {
            jour = "0" + jour;
        }
        if (month < 10) {
            month = "0" + month;
        }
        date = jour + "/" + month + "/" + date_format.getFullYear()
    }
    const includeStops = document.getElementById('includeStops').checked;

    // Vérifier que la date est au bon format (JJ/MM/AAAA)
    const datePattern = /^(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0-2])\/\d{4}$/;
    if (!datePattern.test(date)) {
        Swal.fire({
            title: 'Erreur',
            text: 'Veuillez entrer une date au format JJ/MM/AAAA.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
        return;
    }

    fetch('http://localhost:5000/get_map', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            shiptype: shiptype,
            date: date,
            includeStops: includeStops
        })
    })
        .then(response => response.text())
        .then(data => {
            document.getElementById('contenu').innerHTML = data;
        })
        .catch(error => {
            console.error('Erreur lors de la récupération de la carte:', error); // Affiche les erreurs dans la console
        });

    fetch('http://localhost:5000/get_heatmap', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            shiptype: shiptype,
            date: date,
            includeStops: includeStops
        })
    })
        .then(response => response.text())
        .then(data => {
            document.getElementById('heatmap').innerHTML = data;
        })
        .catch(error => {
            console.error('Erreur lors de la récupération de la carte:', error); // Affiche les erreurs dans la console
        });


});

document.addEventListener('DOMContentLoaded', function () {
    const currentdate = new Date(Date.now());
    let date = currentdate.getDate();
    let month = currentdate.getMonth() + 1;
    if (date < 10) {
        date = "0" + date;
    }
    if (month < 10) {
        month = "0" + month;
    }

    fetch('http://localhost:5000/get_map', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            shiptype: "",
            date: date + "/" + month + "/" + currentdate.getFullYear(),
            includeStops: false
        })
    })
        .then(response => response.text())
        .then(data => {
            document.getElementById('contenu').innerHTML = data;
        })
        .catch(error => {
            console.error('Erreur lors de la récupération de la carte:', error); // Affiche les erreurs dans la console
        });

    fetch('http://localhost:5000/get_heatmap', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            shiptype: "",
            date: date + "/" + month + "/" + currentdate.getFullYear(),
            includeStops: false
        })
    })
        .then(response => response.text())
        .then(data => {
            document.getElementById('heatmap').innerHTML = data;
        })
        .catch(error => {
            console.error('Erreur lors de la récupération de la carte:', error); // Affiche les erreurs dans la console
        });

    flatpickr("#date", {
        dateFormat: "d/m/Y", // Format: JJ/MM/AAAA
        allowInput: false,   // Prevent manual input
        maxDate: "today"     // Optional: Prevent future dates
    });
    const get_shiptype = document.querySelector("select");
    fetch('http://localhost:5000/get_shiptypes', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json()) // Si le backend retourne un JSON
        .then(data => {
            const selectElement = document.getElementById('shiptype-select'); // Assure-toi que l'ID existe dans ton HTML

            // Vider les options existantes
            selectElement.innerHTML = '';

            // Ajouter les nouvelles options récupérées
            data.forEach(shiptype => {
                const option = document.createElement('option');
                option.value = shiptype;
                option.text = shiptype;
                selectElement.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Erreur lors de la récupération des types de navires:', error);
        });
})