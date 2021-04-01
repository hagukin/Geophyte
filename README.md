# 지오파이트(Geophyte) 

![ezgif com-gif-maker](https://user-images.githubusercontent.com/63915665/112706472-b4646500-8ee7-11eb-8d6e-3274e2ce52b5.gif)

게임에 대한 자세한 정보는  링크를 참고해주세요!
https://gamesmith.tistory.com/11?category=945745

---

## 왜 파이썬으로 만들었는가?

지오파이트가 C계열 언어가 아니라 파이썬으로 작성된 이유는 크게 세 가지 입니다.
1. 게임이 지향하는 목표가 거대하고, 또 개발인력은 저 하나뿐이다 보니, 아무래도 C계열 언어들보다는 생산성이 높은 파이썬이 더 적합하다고 판단했습니다.
2. 이 게임의 초창기 버전은 제가 프로그래밍 공부를 시작하고 나서 얼마 지나지 않았을 때부터 개발됐는데, 그 때 제가 처음 배운 프로그래밍 언어가 파이썬이라 지오파이트는 지금까지 자연스럽게 파이썬으로 개발되고 있습니다.
3. numpy 같은 여러 유용한 라이브러리들이 잘 갖추어져 있기 때문에 파이썬을 선택했습니다.

---

## 파이썬으로 만드는 데 어려움은 없었나?

굉장히 많은 어려움들이 있었습니다.
개발하면서 파이썬은 게임 개발, 특히 지오파이트처럼 복잡한 구조를 갖고 있는 게임 개발에는 적합한 언어가 아니라는 것을 여러 차례 느끼고 있습니다.
그 이유는 여러 가지가 있는데,

1. 인터프리터 언어의 속도 상의 한계
2. GIL (Global Interpreter Lock)
3. Dynamic typed language
4. 포인터/레퍼런스의 부재 및 메모리 관리의 어려움
5. Call By Assignment를 강제

정도가 가장 큰 장애물로 느껴졌습니다.

---

## 그러한 어려움을 어떻게 극복했나?

수 많은 시행착오를 거치며 극복해 나갔습니다. 
기억나는 것들을 간추리자면 다음과 같습니다.

1. 자주 활용되는 알고리즘들은 경우 C 기반 라이브러리와 연동해 사용
2. 큰 단위의 계산들에서는 numpy 활용
3. typing 을 적극 지향함으로써 최대한 Static typed language스러운 명료한 구조 형성
4. 구조를 체계적으로 설계하고, 또 수 차례 리팩토링을 반복함으로써 GC(혹은 Reference Count)가 놓쳐 낭비되는 메모리가 없도록 설계

---

## 그 외

게임이 완성되면 외국계 로그라이크 커뮤니티에도 공유할 생각이라 주석은 영어로 작성하고 있습니다. (PEP-8)

한글로 쓴 개발일지가 src/devlog.txt에 기록되어 있으니 참고해주세요.
다만 해당 개발일지는 저 혼자 보고 참고하는 용도로 작성했기 때문에 내용이 읽기 편하게 정돈되어 있지는 않은 점 양해 부탁드립니다.
나중에 시간이 남는다면 블로그에 개발과정을 제대로 포스팅할 계획입니다.
