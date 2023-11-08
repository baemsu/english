import streamlit as st
import pandas as pd
import random

# 데이터셋 로드 (예시 경로입니다. 실제 경로로 변경해주세요.)
DATA_URL = '교육부_3천단어_수정분.txt'

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_URL, sep='\t', encoding='CP949')
    return data

def generate_questions(data, day, question_count):
    # Filter the data for the specified day
    day_data = data[data['일자'].str.strip() == day]

    # Check if day_data is empty or if '단어' column has no valid entries
    if day_data.empty or '단어' not in day_data.columns or day_data['단어'].isnull().all():
        raise ValueError(f"No data available for {day}")

    questions = []
    while len(questions) < question_count:
        question_type = random.choice([1, 2])  # Randomly select question type (1 or 2)
        if question_type == 1:
            # Type 1: "(    ) 영단어는 어떤 의미인가요?"
            word_row = day_data.sample(1)
            word = word_row['단어'].values[0]
            correct_meaning = word_row['뜻'].values[0]
            options = [correct_meaning] + day_data.sample(4)['뜻'].tolist()
            random.shuffle(options)
            question = (f'({len(questions) + 1}) {word} 영단어는 어떤 의미인가요?', correct_meaning, options)
        else:
            # Type 2: "(   ) 뜻을 가진 영단어는 무엇인가요?"
            meaning_row = day_data.sample(1)
            correct_word = meaning_row['단어'].values[0]
            meaning = meaning_row['뜻'].values[0]
            options = [correct_word] + day_data.sample(4)['단어'].tolist()
            random.shuffle(options)
            question = (f'({len(questions) + 1}) {meaning} 뜻을 가진 영단어는 무엇인가요?', correct_word, options)
        if question not in questions:
            questions.append(question)

    return questions



# Streamlit 앱 시작
def main():
    st.title('영단어 학습 테스트')

    # 데이터 로드
    data = load_data()

    # 세션 상태 초기화
    if 'day' not in st.session_state:
        st.session_state.day = None
        st.session_state.score = 0
        st.session_state.total_questions = 0
        st.session_state.answered = False  # 정답 확인 여부를 추적하는 상태
        st.session_state.questions = []  # 질문 리스트 초기화
        st.session_state.current_question_num = 0  # 현재 질문 번호 초기화
        st.session_state.show_start_button = True  # "시작" 버튼 표시 여부 초기화
        st.session_state.show_next_button = False  # "다음 문제" 버튼 표시 여부 초기화
        st.session_state.show_restart_button = False  # "다시 시작" 버튼 표시 여부 초기화

    # 일자 선택
    selected_day = st.selectbox('일자 선택', data['일자'].unique())

    # 출제 문제 수 입력
    question_count = st.number_input('출제 문제 수', min_value=1, max_value=10)

    # "다시 시작" 버튼 클릭 시 초기화
    if st.session_state.show_restart_button and st.button('다시 시작'):
        st.session_state.show_restart_button = False
        st.session_state.show_start_button = True
        st.session_state.day = None
        st.session_state.score = 0
        st.session_state.total_questions = 0
        st.session_state.answered = False
        st.session_state.questions = []
        st.session_state.current_question_num = 0

    # 시작 버튼
    if st.session_state.show_start_button and st.button('시작'):
        st.session_state.day = selected_day
        questions = generate_questions(data, st.session_state.day, question_count)
        st.session_state.questions = questions
        st.session_state.total_questions = len(questions)
        st.session_state.answered = False
        st.session_state.current_question_num = 1
        st.session_state.show_start_button = False
        st.session_state.show_next_button = True

    # 문제가 생성되었는지 확인
    if st.session_state.questions and not st.session_state.answered:
        if st.session_state.current_question_num <= len(st.session_state.questions):
            current_question = st.session_state.questions[st.session_state.current_question_num - 1]
            question_text, correct_answer, options = current_question
            st.write(f'({st.session_state.current_question_num}/{st.session_state.total_questions}) {question_text}')

            # 객관식 옵션 표시
            option = st.radio("보기", options, key="option")

            # 정답 확인 버튼
            if st.button('정답 확인'):
                st.session_state.answered = True
                if option == correct_answer:
                    st.success('정답입니다!')
                    st.session_state.score += 1
                else:
                    st.error(f'오답입니다! 정답은 {correct_answer}입니다.')

    # 다음 문제 버튼 (정답 확인 후에만 활성화)
    if st.session_state.answered and st.session_state.show_next_button:
        if st.session_state.current_question_num < st.session_state.total_questions:
            if st.button('다음 문제'):
                st.session_state.current_question_num += 1
                st.session_state.answered = False
        else:
            st.write(f'총 {st.session_state.total_questions}개 중 {st.session_state.score}개 정답')
            st.write(f'점수: {round((st.session_state.score / st.session_state.total_questions) * 100, 2)}점')
            st.session_state.show_start_button = False
            st.session_state.show_restart_button = True

    # 진행 상황 표시 (progress bar)
    if st.session_state.total_questions > 0:
        progress = st.session_state.current_question_num / st.session_state.total_questions
        st.progress(progress, f'진행 상황: {st.session_state.current_question_num}/{st.session_state.total_questions}')

if __name__ == '__main__':
    main()
