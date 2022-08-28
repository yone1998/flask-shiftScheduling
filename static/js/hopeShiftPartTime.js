{
    let iDay = 1
    while (document.getElementById('day_' + iDay)) {
        const element = document.getElementById('day_' + iDay)

        if (element.checked) {
            document.getElementById('startEmpty' + iDay).style.display = "none"
            document.getElementById('endEmpty' + iDay).style.display = "none"
        } else {
            document.getElementById('start' + iDay).style.display = "none"
            document.getElementById('end' + iDay).style.display = "none"
        }
        iDay += 1

        element.addEventListener('click', function(){
            targetNum = element.id.split('_')[1]
            if (element.checked) {
                document.getElementById('start' + targetNum).style.display = "flex"
                document.getElementById('startEmpty' + targetNum).style.display = "none"
                document.getElementById('end' + targetNum).style.display = "flex"
                document.getElementById('endEmpty' + targetNum).style.display = "none"
            } else {
                document.getElementById('start' + targetNum).style.display = "none"
                document.getElementById('startEmpty' + targetNum).style.display = "flex"
                document.getElementById('end' + targetNum).style.display = "none"
                document.getElementById('endEmpty' + targetNum).style.display = "flex"
            }
        });
    }
}
