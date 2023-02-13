// 검색창 관련 스크립트
// 검색창 내용 입력 후 검색을 누르면 나오는 div 스크립트
// 이 부분은 손을 봐야함


// 버그 리포트
// 1. 내용 입력후 돋보기 모양 클릭시 충녕봇 초기 화면으로 넘어감
// 2. 사이드바 메뉴 선택 후 돋보기 모양을 클릭하면 해당 div로 넘어가지만
// 3. 사이드바 메뉴 선택 된 것(하얀 배경)이 초기화가 안됨

var bDisplay = true;
function serchbtn(){
  var con = document.getElementById("category1");
  var von = document.getElementById("door")
  var btn1 = document.getElementById("btn1")
  var btn2 = document.getElementById("btn2")
  var btn3 = document.getElementById("btn3")
  var text = document.getElementById("serchtext")
  if(con.style.display=='none'){
    con.style.display = 'block';
    von.style.display='none';
    btn1.style.display = 'none';
    btn2.style.display = 'none';
    btn3.style.display = 'none';
    text.style.display = 'block';
  }else{
    con.style.display='block';
    von.style.display='none';
    btn1.style.display = 'none';
    btn2.style.display = 'none';
    btn3.style.display = 'none';
    text.style.display = 'block';
  }
}
function go_index(){
  console.log(1)
  location.href = '/'
}