// Delete Employee
async function deleteEmployee() {
    if (!confirm('Are you sure you want to delete this employee?')) return;
    try {
        const response = await fetch("/api/enmploy/delete/" + employeeId, {
            method: 'DELETE',
            credentials: 'same-origin'
        });
        if (response.ok) {
            alert('Employee deleted successfully!');
            window.location.href = '/action';
        } else {
            const errorText = await response.text();
            alert('Error: ' + (errorText || 'Could not delete employee.'));
        }
    } catch (error) {
        console.error(error);
        alert('Network error. Please try again.');
    }
}

// Open Update Modal with pre-populated data
function openUpdateModal() {
    // Pre-populate form fields with current employee data
    document.getElementById('update_fname').value = "{{ employee.fname }}";
    document.getElementById('update_mname').value = "{{ employee.mname }}";
    document.getElementById('update_lname').value = "{{ employee.lname }}";
    document.getElementById('update_gender').value = "{{ employee.gender }}";
    document.getElementById('update_fanID').value = "{{ employee.fanID }}";
    document.getElementById('update_birthdate').value = "{{ employee.birthdate.strftime('%Y-%m-%d') if employee.birthdate else '' }}";
    document.getElementById('update_phone_number').value = "{{ employee.phone_number }}";
    document.getElementById('update_edu_level').value = "{{ employee.edu_level }}";
    document.getElementById('update_profession').value = "{{ employee.profession }}";
    document.getElementById('update_join_year').value = "{{ employee.join_year.strftime('%Y-%m-%d') if employee.join_year else '' }}";
    document.getElementById('update_work_experience').value = "{{ employee.work_experience }}";
    document.getElementById('update_position_in_group').value = "{{ employee.position_in_group }}";
    document.getElementById('update_work_place').value = "{{ employee.work_place }}";
    document.getElementById('update_work_place_name').value = "{{ employee.work_place_name }}";
    document.getElementById('update_salary').value = "{{ employee.salary }}";
    document.getElementById('update_group_name').value = "{{ employee.group_name }}";
    document.getElementById('update_werada').value = "{{ employee.werada }}";
    document.getElementById('update_kebele').value = "{{ employee.kebele }}";
    document.getElementById('update_house_number').value = "{{ employee.house_number }}";
    updateModal.style.display = 'flex';
}

// Update Employee form submission
updateForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const submitBtn = document.getElementById('updateBtn');
    const originalText = submitBtn.innerText;
    submitBtn.innerText = 'Updating...';
    submitBtn.disabled = true;

    const formData = new FormData(updateForm);
    const formDataObj = {};
    for (let [key, value] of formData.entries()) {
        if (key !== 'employee_id' && key !== 'photo' && key !== 'photoInput') {
            formDataObj[key] = value;
        }
    }

    try {
        const response = await fetch("/api/enmploy/" + employeeId, {
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