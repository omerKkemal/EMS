const modal = document.getElementById('addEmployeeModal');
const form = document.getElementById('addEmployeeForm');
const photoInput = document.getElementById('photoInput');
const updateModal = document.getElementById('updateEmployeeModal');
const updateForm = document.getElementById('updateEmployeeForm');

// Close modals when clicking on background overlay
modal.addEventListener('click', function(e) {
    if (e.target === modal) modal.style.display = 'none';
});
updateModal.addEventListener('click', function(e) {
    if (e.target === updateModal) updateModal.style.display = 'none';
});

// Dropdown toggle
document.querySelectorAll('.dropdown-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const menu = this.nextElementSibling;
        if (menu) menu.classList.toggle('hidden');
    });
});
window.addEventListener('click', function() {
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        menu.classList.add('hidden');
    });
});

// Delete Employee
async function deleteEmployee(id) {
    if (!confirm('Are you sure you want to delete this employee?')) return;
    try {
        const response = await fetch("/api/enmploy/delete/" + id, {
            method: 'DELETE',
            credentials: 'same-origin'
        });
        if (response.ok) {
            alert('Employee deleted successfully!');
            document.getElementById('employee-row-' + id).remove();
        } else {
            const errorText = await response.text();
            alert('Error: ' + (errorText || 'Could not delete employee.'));
        }
    } catch (error) {
        console.error(error);
        alert('Network error. Please try again.');
    }
}

// Open Update Modal and fetch employee data
async function openUpdateModal(id) {
    try {
        // Fetch employee details (you need to create a GET endpoint)
        const response = await fetch('/api/enmploy/' + id, {
            method: 'GET',
            credentials: 'same-origin'
        });
        if (response.ok) {
            const data = await response.json();
            document.getElementById('updateEmployeeId').value = id;
            document.getElementById('update_fname').value = data.fname || '';
            document.getElementById('update_mname').value = data.mname || '';
            document.getElementById('update_lname').value = data.lname || '';
            document.getElementById('update_gender').value = data.gender || '';
            document.getElementById('update_fanID').value = data.fanID || '';
            document.getElementById('update_birthdate').value = data.birthdate || '';
            document.getElementById('update_phone_number').value = data.phone_number || '';
            document.getElementById('update_edu_level').value = data.edu_level || '';
            document.getElementById('update_profession').value = data.profession || '';
            document.getElementById('update_join_year').value = data.join_year || '';
            document.getElementById('update_work_experience').value = data.work_experience || '';
            document.getElementById('update_position_in_group').value = data.position_in_group || '';
            document.getElementById('update_work_place').value = data.work_place || '';
            document.getElementById('update_work_place_name').value = data.work_place_name || '';
            document.getElementById('update_salary').value = data.salary || '';
            document.getElementById('update_group_name').value = data.group_name || '';
            document.getElementById('update_werada').value = data.werada || '';
            document.getElementById('update_kebele').value = data.kebele || '';
            document.getElementById('update_house_number').value = data.house_number || '';
            updateModal.style.display = 'flex';
        } else {
            alert('Could not fetch employee data.');
        }
    } catch (error) {
        console.error(error);
        alert('Network error. Please try again.');
    }
}

// Update Employee form submission
updateForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const submitBtn = document.getElementById('updateBtn');
    const originalText = submitBtn.innerText;
    submitBtn.innerText = 'Updating...';
    submitBtn.disabled = true;

    const id = document.getElementById('updateEmployeeId').value;
    const formData = new FormData(updateForm);
    const formDataObj = {};
    for (let [key, value] of formData.entries()) {
        if (key !== 'employee_id' && key !== 'photo' && key !== 'photoInput') {
            formDataObj[key] = value;
        }
    }

    try {
        const response = await fetch("/api/enmploy/" + id, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formDataObj),
            credentials: 'same-origin'
        });
        if (response.ok) {
            alert('Employee updated successfully!');
            updateModal.style.display = 'none';
            location.reload();
        } else {
            const errorText = await response.text();
            alert('Error: ' + (errorText || 'Could not update employee.'));
        }
    } catch (error) {
        console.error(error);
        alert('Network error. Please try again.');
    } finally {
        submitBtn.innerText = originalText;
        submitBtn.disabled = false;
    }
});

// Add Employee form submission
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
    });
}

form.addEventListener('submit', async function(e) {
    e.preventDefault();
    const submitBtn = document.getElementById('submitBtn');
    const originalText = submitBtn.innerText;
    submitBtn.innerText = 'Saving...';
    submitBtn.disabled = true;
    const formDataObj = {};
    const formElements = form.elements;
    for (let i = 0; i < formElements.length; i++) {
        const el = formElements[i];
        if (el.name && el.name !== '') formDataObj[el.name] = el.value;
    }
    if (photoInput.files.length > 0) {
        const base64Photo = await fileToBase64(photoInput.files[0]);
        formDataObj.photo = base64Photo;
    }
    try {
        const response = await fetch("/api/employ", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formDataObj),
            credentials: 'same-origin'
        });
        if (response.ok) {
            alert('Employee added successfully!');
            modal.style.display = 'none';
            form.reset();
            photoInput.value = '';
            location.reload();
        } else {
            const errorText = await response.text();
            alert('Error: ' + (errorText || 'Could not add employee.'));
        }
    } catch (error) {
        console.error(error);
        alert('Network error. Please try again.');
    } finally {
        submitBtn.innerText = originalText;
        submitBtn.disabled = false;
    }
});