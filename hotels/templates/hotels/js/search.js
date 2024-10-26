// static/hotels/js/search.js
document.addEventListener('DOMContentLoaded', function() {
    // Handle room configuration updates
    const roomCountSelect = document.getElementById('id_room_count');
    if (roomCountSelect) {
        roomCountSelect.addEventListener('change', function() {
            updateRoomConfigurations(this.value);
        });
    }

    // Date validation
    const checkInInput = document.getElementById('id_check_in');
    const checkOutInput = document.getElementById('id_check_out');
    
    if (checkInInput && checkOutInput) {
        checkInInput.addEventListener('change', function() {
            const checkInDate = new Date(this.value);
            const minCheckOutDate = new Date(checkInDate);
            minCheckOutDate.setDate(checkInDate.getDate() + 1);
            
            checkOutInput.min = minCheckOutDate.toISOString().split('T')[0];
            if (new Date(checkOutInput.value) <= checkInDate) {
                checkOutInput.value = minCheckOutDate.toISOString().split('T')[0];
            }
        });
    }

    // Filter form handling
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const searchParams = new URLSearchParams(formData);
            
            // Preserve existing search parameters
            const currentParams = new URLSearchParams(window.location.search);
            for (let [key, value] of currentParams) {
                if (!searchParams.has(key)) {
                    searchParams.append(key, value);
                }
            }
            
            window.location.search = searchParams.toString();
        });
    }
});

function updateRoomConfigurations(roomCount) {
    const container = document.getElementById('roomConfigurations');
    if (!container) return;

    const template = container.children[0].cloneNode(true);
    container.innerHTML = '';
    
    for (let i = 0; i < roomCount; i++) {
        const room = template.cloneNode(true);
        room.querySelector('h5').textContent = `Room ${i + 1}`;
        room.dataset.room = i;
        
        const inputs = room.querySelectorAll('input');
        inputs.forEach(input => {
            const originalName = input.name.split('_')[0];
            input.name = `${originalName}_${i}`;
            input.id = `id_${originalName}_${i}`;
        });
        
        container.appendChild(room);
    }
}