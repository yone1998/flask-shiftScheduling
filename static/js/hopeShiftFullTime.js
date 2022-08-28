{
    let iDay = 1
    while (document.getElementById('dayLabel' + iDay)) {
        const checkbox = document.getElementById('day'+iDay);
        const label = document.getElementById('dayLabel' + iDay)
        if (checkbox.checked) {
            label.style.backgroundColor = 'rgb(245, 245, 245)'
        } else {
            label.style.backgroundColor = 'pink'
        }

        checkbox.addEventListener('click', function(){
            if (checkbox.checked) {
                label.style.backgroundColor = 'rgb(245, 245, 245)'
            } else {
                label.style.backgroundColor = 'pink'
            }
        });

        iDay += 1
    }
}
