var certificationName;

function showSection(section) {
    document.querySelectorAll('.main-section').forEach(s => {
        s.classList.add('hidden');
    });
    document.getElementById(section).classList.remove('hidden');
    document.getElementById('home-content').style.display = 'none';
    window.location.hash = section;
}

function handleClick(section) {
    showSection(section);

    // Add any additional function calls here based on the section
    switch(section) {
        case 'dashboard':
            showUserDashboard();
            break;
        case 'enrollment':
            showEnrollmentData();
            loadProviders();
            break;
        case 'leadership':
            showOverallChamp();
            fetchData('AWS');
            showProviders();
            break;
        case 'Vouchers':
             getRegistration();
             break;
        case 'upload-certificate':
             loadProviders();
             break;
    }

    // Prevent default link behavior
    return false;
}

document.addEventListener('DOMContentLoaded', function() {
    if (window.location.hash) {
        var section = window.location.hash.substring(1);
        handleClick(section);
    }
});

window.addEventListener('hashchange', function() {
    var section = window.location.hash.substring(1);
    handleClick(section);
});


    function showEnrollment() {
                // Hide all main sections
                document.querySelectorAll('.main-section').forEach(s => {
                    s.classList.add('hidden'); // Hide all sections
                });
                // Show the exam preparation section
                document.getElementById('enrollment').classList.remove('hidden'); // Make exam preparation visible
                // Hide home content when navigating to exam preparation
                document.getElementById('home-content').style.display = 'none'; // Hide home content
            }
            function showCerteHome() {
            const sections = document.querySelectorAll('.main-section');
            sections.forEach(section => {
                section.classList.add('hidden');
            });
            // Show the home content section
            const homeContent = document.getElementById('home-content');
            if (homeContent) {
                homeContent.classList.remove('hidden');
                homeContent.style.display = 'block'; // Ensure it's displayed
                homeContent.style.height = 'calc(100vh - 100px)';
            }
        }
//leadership data changes
    function showProviders() {
     // Fetch initial providers
     $.ajax({
       url: '/get_providers/', // Replace with your Django view URL
       success: function(data) {
         $('#companyDropdown').empty();
         $.each(data, function(index,provider) {
           $('#companyDropdown').append('<option value="' + provider + '">' + provider + '</option>');
         });
       }
     });
     }
    function showOverallChamp(){
    const tbody = document.getElementById("champTableBody");
    fetch( '/get_overall_cert_champ/')
		.then(response => response.json())
		.then(data => {
		tbody.innerHTML = ''; // Clear existing data
		const medalColors = ['gold', 'silver', 'bronze'];
		let rank=0;
		if (data.length < 1){
		tbody.insertAdjacentHTML('beforeend',`<tr>"OOPS! No certification completion record found"</tr>`);
		}
		else {
		data.forEach(employee=>
        {
		const row=document.createElement('tr');
		const nameCell=document.createElement('td');
		const certCell=document.createElement('td');
		const rankCell=document.createElement('td');
		nameCell.textContent=employee.employee_name;
		certCell.textContent=employee.cert_count;
		rankCell.innerHTML = `<i class="fas fa-medal medal" style="color: ${medalColors[rank++]};"></i>`;
		row.appendChild(nameCell);
		row.appendChild(certCell);
		row.appendChild(rankCell);
		tbody.appendChild(row);
		});
		}
		})
		.catch(error =>{
		console.error('Error fetching data:',error);
		});
    };
    // Function to fetch and display data
    function fetchData(category){
        const companyDropdown = document.getElementById("companyDropdown");
        const companyName = companyDropdown.value;
        const tbody=document.getElementById("providerTableBody");
        const h1Element=document.getElementById("leadershiph1");
        fetch( '/get_employee_data/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ 'category': category })
        })
		.then(response => response.json())
		.then(data => {
		tbody.innerHTML = ''; // Clear existing data
		const quarter=data.quarter_data.quarter;
		const year=data.quarter_data.year;
		const emp_data=data.emp_data;
		h1Element.textContent = `Associates Certified in Q${quarter}, ${year}`;
		if (emp_data.length < 1){
		tbody.insertAdjacentHTML('beforeend',`<tr><td>"OOPS! No one completed certification for this Provider"</td></tr>`);
		}
		else {
		emp_data.forEach(employee=>
        {
		const row=document.createElement('tr');
		const nameCell=document.createElement('td');
		nameCell.textContent=employee.employee_name;
		const psnoCell=document.createElement('td');
		psnoCell.textContent=employee.employee_ps_no;
		row.appendChild(psnoCell);
		row.appendChild(nameCell);
		tbody.appendChild(row);
		});
		}
		})
		.catch(error =>{
		console.error('Error fetching data:',error);
		});
    }
    //add event listener on dropdown change
     document.getElementById("companyDropdown").addEventListener('change',function(){
     const selectedCategory=this.value;
     fetchData(selectedCategory);
     });

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

        const alertContainer = document.getElementById('alert-container');
        const loginMessage = sessionStorage.getItem('loginMessage');
        const logoutMessage = sessionStorage.getItem('logoutMessage');

        if (loginMessage) {
            alertContainer.innerHTML += `<div class="alert alert-success">${loginMessage}</div>`;
            sessionStorage.removeItem('loginMessage'); // Clear message after displaying
        }

        if (logoutMessage) {
            alertContainer.innerHTML += `<div class="alert alert-info">${logoutMessage}</div>`;
            sessionStorage.removeItem('logoutMessage'); // Clear message after displaying
        }

        // Handle logout link click
//        document.getElementById('logout-link').addEventListener('click', function(event) {
//            event.preventDefault(); // Prevent default anchor behavior
//
//             Simulate logout
//            sessionStorage.setItem('logoutMessage', 'You have been logged out.');
//            window.location.href = 'login.html'; // Redirect to the login page or home page
//        });
    //functions for dynamic certification data
    function loadProviders() {
     // Fetch initial providers
     $.ajax({
       url: '/get_providers/', // Replace with your Django view URL
       success: function(data) {
         $('#provider').empty();
         $('#provider1').empty();
          $('#provider').append('<option value=" "> --Select Provider-- </option>');
          $('#provider1').append('<option value=" ">--Select Provider-- </option>');
         $.each(data, function(index,provider) {
           $('#provider').append('<option value="' + provider + '">' + provider + '</option>');
           $('#provider1').append('<option value="' + provider + '">' + provider + '</option>');
         });
       }
     });
     }
    function loadNames() {
        const providerElement=document.getElementById("provider");
        const provider=providerElement.value;
        $.ajax({
            url: '/get_names/',
            data: {
                'provider': provider
            },
            success: function(data) {
                console.log('Received data:', data);
                $('#name').empty();
                $.each(data, function(index, item) {
                    $('#name').append('<option value="' + item[1] + '">' + item[1] + '</option>');
                });
            },
            error: function(xhr, status, error) {
                console.error('AJAX error:', status, error);
            }
        });
      }
 function loadNamesCertUpload() {
        const providerElement=document.getElementById("provider1");
        const provider=providerElement.value;
        $.ajax({
            url: '/get_names/',
            data: {
                'provider': provider
            },
            success: function(data) {
                console.log('Received data:', data);
                $('#name1').empty();
                $.each(data, function(index, item) {
                    $('#name1').append('<option value="' + item[1] + '">' + item[1] + '</option>');
                });
            },
            error: function(xhr, status, error) {
                console.error('AJAX error:', status, error);
            }
        });
      }
    function showEnrollmentData(){
    const tbody = document.getElementById("enrollTableBody");
    fetch( '/show_enrollment/')
		.then(response => response.json())
		.then(data => {
		tbody.innerHTML = ''; // Clear existing data
		data.forEach(enrolldata=>
        {
		const row=document.createElement('tr');
		const nameCell=document.createElement('td');
		const statusCell=document.createElement('td');
		nameCell.textContent=enrolldata.certification_name;
		statusCell.textContent=enrolldata.certification_status;
		row.appendChild(nameCell);
		row.appendChild(statusCell);
		tbody.appendChild(row);
		});
		})
		.catch(error =>{
		console.error('Error fetching data:',error);
		});
    };
    function getRegistration() {
    $.ajax({
        url: '/show_enrollment/',
        success: function(data) {
            console.log('Received data:', data);
            data = data.filter(item => item.certification_status !== 'Failed');
            $('#registered_cert_dropdown').empty();
            $('#registered_cert_dropdown').append('<option value=" ">--Select option--</option>');
            $.each(data, function(index, item) {
                $('#registered_cert_dropdown').append('<option value="' + item['certification_name'] + '">' + item['certification_name'] + '</option>');
            });
            $('#registered_cert_dropdown').on('change', function() {
                certificationName = $(this).val();
                const selectedData = data.find(item => item.certification_name === certificationName);
                if (selectedData) {
                    const status = selectedData.certification_status;
                    const voucher = selectedData.voucher_code;
                    console.log(status);
                    const statusElement=document.getElementById("statusmessage");
                     $('#voucherreceivedbtn').text('Voucher Received').css('background-color', '');
                    $('.step-navigation button').prop('disabled', true).addClass('disabled-button').removeClass('active');
                    // Update button states based on status
                    if (status === 'enrolled') {
                        $('#requestwcptestbtn').prop('disabled', false).removeClass('disabled-button').addClass('active');
                        statusElement.textContent=""
                    } else if (status === 'WCP Test Requested') {
                        statusElement.textContent="WCP Requested.Awaiting response."
                    }else if (status === 'WCP Assigned') {//
                        $('#wcpcompletedbtn').prop('disabled', false).removeClass('disabled-button').addClass('active');
                        statusElement.textContent="WCP assigned,please complete it and click on WCP completed Button";
                    } else if (status === 'WCP Completed') {//
                        statusElement.textContent="Validating your WCP score! Please wait.";
                    }else if (status === 'Voucher Assigned') {//
                        $('#exambookedbtn').prop('disabled', false).removeClass('disabled-button').addClass('active');
//                        $('#voucherreceivedbtn').prop('disabled', false).removeClass('disabled-button').addClass('active');
//                        statusElement.textContent="Voucher ${voucher} assigned, book your exam and click on Exam Booked Button";
                        statusElement.textContent=`Voucher ${voucher} assigned to you, book your exam and click on Exam Booked Button`;
                    }else if (status=== 'Exam Booked'){//
                        $('#examdatebtn').prop('disabled', false).addClass('active').removeClass('disabled-button');
                        statusElement.textContent="";
                    }
                    else if (status=== 'WCP Failed'){//
                        $('#voucherreceivedbtn').text('WCP Failed').css('background-color','red');
                        statusElement.textContent=" Sorry you haven't cleared WCP exam !!!";
                    }
                    else if (status=== 'Exam Date Set'){//
                        $('#examdatebtn').prop('disabled', false).addClass('active').removeClass('disabled-button');
                        statusElement.textContent="Make sure you updated correct exam Date";
                    }
                    else if (status=== 'Failed'){//
                        statusElement.textContent="OOPS!!! You haven't cleared certification";
                    }
                    else if (status=== 'Completed'){//
                        statusElement.textContent="Congrats!!! You have cleared certification";
                    }
                } else {
                    console.log('Selected data not found');
                }
            });
        },
        error: function(xhr, status, error) {
            console.error('AJAX error:', status, error);
        }
    });
}

$(document).ready(function() {
    // Add click event listeners to all buttons
    $('.step-navigation button').click(function() {
        var buttonId = $(this).attr('id');
        var newStatus;

        // Determine the new status based on which button was clicked
        switch(buttonId) {
            case 'requestwcptestbtn':
                newStatus = 'WCP Test Requested';
                break;
            case 'wcpcompletedbtn':
                newStatus = 'WCP Completed';
                break;
            case 'exambookedbtn':
                newStatus = 'Exam Booked';
                break;
            case 'examdatebtn':
                newStatus = 'Exam Date Set';
                break;
        }

        console.log(certificationName);

        // Send AJAX request to update status
        $.ajax({
            url: '/update_certification_status/',
            method: 'POST',
            data: {
                certification_name: certificationName,
                new_status: newStatus
            },
            success: function(response) {
                console.log('Status updated successfully',newStatus);
                updateButtonStates(newStatus);// Update UI to reflect new status
            },
            error: function(xhr, status, error) {
                console.error('Error updating status:', error);
            }
        });
    });
});
    function updateButtonStates(status) {
    // Disable all buttons
    $('.step-navigation button').prop('disabled', true).addClass('disabled-button').removeClass('active');
    const statusElement=document.getElementById("statusmessage");

    // Enable the appropriate next button based on the new status
    switch(status) {
        case 'WCP Test Requested':
//            $('.step-navigation button').prop('disabled', true).addClass('disabled-button').removeClass('active');
            statusElement.textContent="WCP Requested.Awaiting response."
            break;
        case 'WCP Completed':
//            $('.step-navigation button').prop('disabled', true).addClass('disabled-button').removeClass('active');
            statusElement.textContent="Validating your WCP score! Please wait.";
            break;
        case 'Exam Booked':
            $('#examdatebtn').prop('disabled', false).addClass('active').removeClass('disabled-button');
            statusElement.textContent="";
            break;
        case 'Exam Date Set':
          $('#examdatebtn').prop('disabled', false).addClass('active').removeClass('disabled-button');
          statusElement.textContent="Make sure you updated correct exam Date";
          break;

    }
}

function showDateDiv(){
    var dateDiv=document.getElementById("dateDiv");
    dateDiv.style.display = "block";
}
$(document).ready(function() {
    $('#dateSubmitBtn').click(function(e) {
        e.preventDefault(); // Prevent the default form submission

        const dateInput = document.getElementById('date');
        const selectedDateStr = dateInput.value;
        const selectedDate = new Date(selectedDateStr);

        if (isNaN(selectedDate.getTime())) {
            console.error("Invalid date format.");
        } else {
            const year = selectedDate.getFullYear();
            const month = selectedDate.getMonth() + 1;
            const day = selectedDate.getDate();

            const formattedDate = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
            console.log("Selected Date:", formattedDate);

            $.ajax({
                url: '/update_exam_date/',
                method: 'POST',
                data: {
                    certification_name: certificationName,
                    date: formattedDate
                },
                success: function(response) {
                    console.log('Status updated successfully', response.newStatus);
                    updateButtonStates(response.newStatus);
                    $('#dateDiv').hide();
                },
                error: function(xhr, status, error) {
                    console.error('Error updating status:', error);
                }
            });
        }
    });
});
//Update User Dashboard
 function updateUserDashboard() {
    $.ajax({
        url: '/show_enrollment/',
        success: function(data) {
            console.log('Received data:', data);
            $('#registered_cert_dropdown').empty();
            $.each(data, function(index, item) {
                $('#registered_cert_dropdown').append('<option value="' + item['certification_name'] + '">' + item['certification_name'] + '</option>');
            });
            $('#registered_cert_dropdown').on('change', function() {
                certificationName = $(this).val();
                const selectedData = data.find(item => item.certification_name === certificationName);
                if (selectedData) {
                    const status = selectedData.certification_status;
                    console.log(status);
                    const statusElement=document.getElementById("statusmessage");
                     $('#voucherreceivedbtn').text('Voucher Received').css('background-color', '');
                    $('.step-navigation button').prop('disabled', true).addClass('disabled-button').removeClass('active');
                    // Update button states based on status
                    if (status === 'enrolled') {
                        $('#requestwcptestbtn').prop('disabled', false).removeClass('disabled-button').addClass('active');
                        statusElement.textContent=""
                    } else if (status === 'WCP Test Requested') {
                        statusElement.textContent="WCP Requested.Awaiting response."
                    }else if (status === 'WCP Assigned') {//
                        $('#wcpcompletedbtn').prop('disabled', false).removeClass('disabled-button').addClass('active');
                        statusElement.textContent="WCP assigned,please complete it and click on WCP completed Button";
                    } else if (status === 'WCP Completed') {//
                        statusElement.textContent="Validating your WCP score! Please wait.";
                    }else if (status === 'Voucher Assigned') {//
                        $('#exambookedbtn').prop('disabled', false).removeClass('disabled-button').addClass('active');
//                        $('#voucherreceivedbtn').prop('disabled', false).removeClass('disabled-button').addClass('active');
                        statusElement.textContent="Voucher sent over email, book your exam and click on Exam Booked Button";
                    }else if (status=== 'Exam Booked'){//
                        $('#examdatebtn').prop('disabled', false).addClass('active').removeClass('disabled-button');
                        statusElement.textContent="";
                    }
                    else if (status=== 'WCP Failed'){//
                        $('#voucherreceivedbtn').text('WCP Failed').css('background-color','red');
                        statusElement.textContent=" Sorry you haven't cleared WCP exam !!!";
                    }
                    else if (status=== 'Exam Date Set'){//
                        $('#examdatebtn').prop('disabled', false).addClass('active').removeClass('disabled-button');
                        statusElement.textContent="Make sure you updated correct exam Date";
                    }
                    else if (status=== 'Failed'){//
                        statusElement.textContent="OOPS!!! you haven't cleared certification.";
                    }
                    else if (status=== 'Completed'){//
                        statusElement.textContent="Congrats!!! you cleared certification.";
                    }
                }
                else {
                    console.log('Selected data not found');
                }
                
            });
        },
        error: function(xhr, status, error) {
            console.error('AJAX error:', status, error);
        }
    });
}

function showUserDashboard(){
    const tbody = document.getElementById("userdashboardtbody");
    const pcomp = document.getElementById("completioncount");
    const pvoucher = document.getElementById("vouchercount");
    fetch( '/show_enrollment/')
		.then(response => response.json())
		.then(data => {
		const counts = data.reduce((counts, item) => {
        if (item.certification_status === "Completed") {
            counts.completed++;
        }
        if (item.voucher_code !== null) {
             counts.voucherass++;
        }
        return counts;
        }, { completed: 0, voucherass: 0 });

        pcomp.innerHTML = ''; // Clear existing data
		pcomp.innerHTML = counts.completed;

		pvoucher.innerHTML = ''; // Clear existing data
		pvoucher.innerHTML = counts.voucherass;

		tbody.innerHTML = ''; // Clear existing data
		tbody.innerHTML = generateTableRows(data);
		})
		.catch(error =>{
		console.error('Error fetching data:',error);
		});
    };

 function generateTableRows(enrollmentData) {
  return enrollmentData.map(record => {
    let statusCells = '';

    if (['enrolled', 'WCP Assigned', 'WCP Test Requested'].includes(record.certification_status)) {
      statusCells = '<td>❌</td><td>❌️</td><td>❌</td><td>❌</td><td>❌</td>';
    } else if (record.certification_status === 'Completed') {
      statusCells = '<td>✔️</td><td>✔️</td><td>✔️</td><td>✔️</td><td>✔️</td>';
    } else if (['WCP Completed', 'WCP Failed'].includes(record.certification_status)) {
      statusCells = '<td>✔️</td><td>❌️</td><td>❌️</td><td>❌️</td><td>❌️</td>';
    } else if (['Voucher Assigned', 'Exam Booked', 'Exam Date Set'].includes(record.certification_status)) {
      statusCells = '<td>✔️</td><td>️️️✔️</td><td>❌️</td><td>❌️</td><td>❌️</td>';
    } else if (record.certification_status === 'Failed') {
      statusCells = '<td>✔️</td><td>✔️</td><td>✔️</td><td>❌️</td><td>❌️</td>';
    }

    // Split the statusCells into an array
    let cellsArray = statusCells.split('</td><td>');

    // If voucher_code is not present, set the third cell (index 2) to ❌
    if (!record.voucher_code) {
      cellsArray[1] = '❌';
    }

    // Join the cells back into a string
    statusCells = cellsArray.join('</td><td>');

    return `
      <tr>
        <td>${record.certification_name}</td>
        ${statusCells}
      </tr>
    `;
  }).join('');
}
function showUploadOptions() {
    document.getElementById('uploadStatus').style.display = 'block';
}
function showExamStatus() {
    document.getElementById('examStatus').style.display = 'block';
}
function updateSubmitButtonState() {
    const submitButton = document.getElementById('submitButton');
    const examFail = document.getElementById('fail');
    console.log(examFail);

    if (examFail.checked) {
        submitButton.removeAttribute('disabled');
        submitButton.classList.remove('disabled-button');
    } else {
        submitButton.disabled = true;
        submitButton.classList.add('disabled-button');
    }
}

// function to the 'pass' radio button
function handleFailOption() {
    updateSubmitButtonState();
}

function handlePassOption() {
    updateSubmitButtonState();
}

function showHardcodedLink() {
    document.getElementById('requestIdInput').style.display = 'none';
    document.getElementById('hardcodedLink').style.display = 'block';
    document.getElementById('requestIdValue').value = ''; // Clear the input field
}

function handleRequestIdChange(isYes) {
    document.getElementById('requestIdInput').style.display = isYes ? 'block' : 'none';
    document.getElementById('hardcodedLink').style.display = isYes ? 'none' : 'block';
    document.getElementById('uploadStatus').style.display = 'block';
    document.getElementById('uploadConfirm').checked = false;
     disableSubmitButton()
}

function disableSubmitButton() {
    const submitButton = document.getElementById('submitButton');
    submitButton.disabled = true;
    submitButton.classList.add('disabled-button');
}
function toggleSubmitButton() {
    const submitButton = document.getElementById('submitButton');
    const uploadConfirm = document.getElementById('uploadConfirm');
    const examFail = document.getElementById('fail');
    const isChecked = uploadConfirm || examFail;
    submitButton.disabled = !isChecked;
    if (isChecked) {
        submitButton.classList.remove('disabled-button');
    } else {
        submitButton.classList.add('disabled-button');
    }
}

function showRequestIdOptions() {
    document.getElementById('requestIdOptions').style.display = 'block';
}

function hideRequestIdOptions() {
    document.getElementById('requestIdOptions').style.display = 'none';
    document.getElementById('submitButton').disabled = true;
}

//Enrollment data changes
    function saveEnrollment() {
    const provider=document.getElementById('provider').value;
    const name=document.getElementById('name').value;
    dataToSend={'provider':`${provider}`,'name':`${name}`}
    console.log(dataToSend)
    fetch('/save_enrollment/', {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
       'X-CSRFToken': getCookie('csrftoken')
     },
     body: JSON.stringify(dataToSend)  // Convert the object to a JSON string
    })
    .then(response => response.json())
    .then(data => {
       if (data.status === 'success') {
           alert(data.message);
            window.location.reload();
       } else if (data.status === 'error') {
           alert(data.message);
       }else if (data.status === 'exist') {
           alert(data.message);
       }
    });
     }

