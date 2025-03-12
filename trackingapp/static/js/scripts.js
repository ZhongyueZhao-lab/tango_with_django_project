/* 文件路径: trackingapp/static/js/scripts.js */

// Toast 通知功能
function showToast(message, type = 'info') {
    const toastHTML = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    const toastContainer = document.getElementById('toast-container') || (() => {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
        return container;
    })();

    const toastElement = document.createElement('div');
    toastElement.innerHTML = toastHTML;
    toastContainer.appendChild(toastElement.firstElementChild);
    
    const toast = new bootstrap.Toast(toastContainer.lastElementChild, {
        autohide: true,
        delay: 3000
    });
    toast.show();
}

// 加载指示器
function showLoading(show = true) {
    let loader = document.getElementById('global-loader');
    if (!loader && show) {
        loader = document.createElement('div');
        loader.id = 'global-loader';
        loader.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center bg-white bg-opacity-75';
        loader.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        `;
        document.body.appendChild(loader);
    } else if (loader && !show) {
        loader.remove();
    }
}

// 考勤标记功能
async function markAttendance() {
    try {
        const courseSelect = document.getElementById('course_id');
        const courseId = courseSelect ? courseSelect.value : '';
        const studentEl = document.getElementById('student_id');
        const studentId = studentEl ? studentEl.value : '';
        const status = document.getElementById('attendance_status').value;

        // If on student side, hidden input student_id = user.id
        // If on teacher side, need to select student from dropdown
        // Both must be non-empty
        if (!courseId || !status) {
            showToast('Please fill out or select course and status', 'danger');
            return;
        }
        if (!studentId) {
            showToast('Please select (or auto-fill) the student ID', 'danger');
            return;
        }

        showLoading(true);

        const response = await $.ajax({
            url: '/attendance/mark/' + courseId + '/',
            type: 'POST',
            data: {
                'student_id': studentId,
                'status': status,
                'csrfmiddlewaretoken': getCookie('csrftoken')
            }
        });

        showToast('Attendance marked successfully', 'success');
        location.reload();

    } catch (error) {
        console.error(error);
        showToast('Failed to mark attendance: ' + (error.responseText || 'Please check your input'), 'danger');
    } finally {
        showLoading(false);
    }
}

// 生成二维码功能
async function generateQRCode() {
    try {
        const courseId = document.getElementById('qr_course_id').value;
        
        if (!courseId) {
            showToast('Please select a course', 'danger');
            return;
        }

        showLoading(true);
        
        const response = await $.ajax({
            url: '/attendance/qr/' + courseId + '/',
            type: 'GET',
            xhrFields: {
                responseType: 'arraybuffer'
            }
        });

        const base64Image = btoa(
            new Uint8Array(response)
            .reduce((data, byte) => data + String.fromCharCode(byte), '')
        );

        const qrWrapper = document.getElementById('qr_image_wrapper');
        const imgHTML = `
            <div class="card shadow-sm fade-in">
                <div class="card-body text-center">
                    <img src="data:image/png;base64,${base64Image}" 
                         alt="QR Code" 
                         class="img-fluid"
                         style="max-width: 300px">
                    <p class="mt-3 mb-0 text-muted">Course Attendance QR Code</p>
                </div>
            </div>
        `;
        
        qrWrapper.innerHTML = imgHTML;
        showToast('QR Code generated successfully', 'success');

    } catch (error) {
        console.error(error);
        showToast('Failed to get QR Code', 'danger');
    } finally {
        showLoading(false);
    }
}

// Django CSRF Token 获取函数
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

// 文档加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有工具提示
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });

    // 初始化所有下拉菜单
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(dropdown => {
        new bootstrap.Dropdown(dropdown);
    });
});

/* NEW CODE for teacher side:
   当教师/管理员选择了某门课程后, 只显示该course的学生 */
function filterStudentList() {
    const courseSelect = document.getElementById('course_id');
    const selectedCourseId = courseSelect ? courseSelect.value : '';

    const studentSelect = document.getElementById('student_id');
    if (!studentSelect) return;

    // 遍历 studentSelect 下所有 <option>
    for (const opt of studentSelect.options) {
        const optCourse = opt.getAttribute('data-course');
        // 如果 <option> 没有 data-course, 可能是占位"请选择学生", 直接显示
        if (!optCourse) {
            opt.hidden = false;
            continue;
        }
        // 如果 optCourse 与 selectedCourseId 匹配, 显示; 否则隐藏
        if (optCourse === selectedCourseId) {
            opt.hidden = false;
        } else {
            opt.hidden = true;
        }
    }
    // 重置一下下拉的选中值
    studentSelect.value = '';
}
