new Vue({
    el:"#createWorkDaySelect",
    data:{
    },
    created() {
        let iDay = 1
        while (document.getElementById('dayLabel' + iDay)) {
            const element = document.getElementById('dayLabel' + iDay)
            console.log('test')
            console.log(window.getComputedStyle(element).color)
            if (element.classList.contains("isHopeDay")) {
                element.style.backgroundColor = 'rgb(245, 245, 245)'
            } else {
                element.style.backgroundColor = 'pink'
            }
            iDay += 1
        }
    },
    methods:{
        switchHopeDay:function(event){
            const element = event.target
            if (element.classList.contains("isHopeDay")) {
                element.classList.remove("isHopeDay")
                element.style.backgroundColor = 'pink'
            } else {
                element.classList.add("isHopeDay")
                element.style.backgroundColor = 'rgb(245, 245, 245)'
            }
        }
    },
    delimiters: ['[[', ']]']
})
