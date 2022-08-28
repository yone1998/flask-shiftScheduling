{
    const today = new Date()
    const SMTWTFS = ["日", "月", "火", "水", "木", "金", "土"]
    const FIRST_DAY_OF_TARGET_MONTH =  new Date(today.getFullYear(), today.getMonth()+1, 1);
    const FIRST_SUNDAY_TARGET_MONTH = (SMTWTFS.length - FIRST_DAY_OF_TARGET_MONTH.getDay()) % SMTWTFS.length + 1;
    let iDay = 1
    while (document.getElementById('dayLabel' + iDay)) {
        const element = document.getElementById('dayLabel' + iDay)

        if ((iDay - FIRST_SUNDAY_TARGET_MONTH) % SMTWTFS.length == 0) {
            element.classList.add('red')
        } else if ((iDay - FIRST_SUNDAY_TARGET_MONTH + 1) % SMTWTFS.length == 0) {
            element.classList.add('blue')
        }

        iDay += 1
    }
}
