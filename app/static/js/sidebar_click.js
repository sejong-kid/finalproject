// 사이드바 각 메뉴 선택시 하얀 배경 유지하는 스크립트
// 이걸로 각 메뉴 선택 이후 나오는 div의 상단 버튼들도 색상 변경을 해야하는데
// 이 스크립트의 내용을 이해하지 못해서 지정하지 못함.
let list = document.querySelectorAll('.list');
for (let i=0; i<list.length; i++){
  list[i].onclick = function(){
    let j = 0;
    while(j < list.length){
      list[j++].className='list';
    }
    list[i].className = 'list active';
  }
}


// 아래의 스크립트를 간결하게 할 수 있을 것 같은데....
// 채용 및 모집 클릭시 다른 div 숨기기
