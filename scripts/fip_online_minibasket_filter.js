{
  let YEARS = ["2018", "2017"]
  let ROW_SELECTOR = "tr.GL0NKRWDHK, tr.GL0NKRWDHL"
  let BIRTH_DATE_SELECTOR = "div.GL0NKRWDIYG"
  let CNT_SELECTOR = "div.GL0NKRWDH0J"

  let rows = document.querySelectorAll(ROW_SELECTOR)
  let cnt = 0

  rows.forEach((el) => {
    let birth_date = el.querySelector(BIRTH_DATE_SELECTOR).textContent

    let condition = YEARS.some((value) => {
      return birth_date.includes(value)
    })
    // console.log(`${birth_date} --> ${condition}`)
    
    if (condition){
      cnt += 1
    }
    else {
       el.hidden = true
    }
  })
  
  document.querySelectorAll(CNT_SELECTOR)[1].textContent = cnt
}