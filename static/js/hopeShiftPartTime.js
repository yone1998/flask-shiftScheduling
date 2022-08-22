new Vue({
    el:"#workTimeSelect",
    data:{
    },
    created() {
        let iDay = 1
        while (document.getElementById('hopeDayCheckBox_' + iDay)) {
            element = document.getElementById('hopeDayCheckBox_' + iDay)
            if (element.classList.contains("isHopeDay")) {
                document.getElementById('startEmpty' + iDay).style.display = "none"
                document.getElementById('endEmpty' + iDay).style.display = "none"
            } else {
                document.getElementById('start' + iDay).style.display = "none"
                document.getElementById('end' + iDay).style.display = "none"
            }
            iDay += 1
        }
    },
    methods:{
        switchHopeDay: function(event) {
            element = event.target
            targetNum = element.id.split('_')[1]
            if (element.classList.contains("isHopeDay")) {
                element.classList.remove("isHopeDay")
                document.getElementById('start' + targetNum).style.display = "none"
                document.getElementById('startEmpty' + targetNum).style.display = "flex"
                document.getElementById('end' + targetNum).style.display = "none"
                document.getElementById('endEmpty' + targetNum).style.display = "flex"
            } else {
                element.classList.add("isHopeDay")
                document.getElementById('start' + targetNum).style.display = "flex"
                document.getElementById('startEmpty' + targetNum).style.display = "none"
                document.getElementById('end' + targetNum).style.display = "flex"
                document.getElementById('endEmpty' + targetNum).style.display = "none"
            }
        }
    },
    delimiters: ['[[', ']]']
})
