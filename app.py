from flask import Flask, render_template, request, redirect, url_for
import os
from coolway.runner import run_from_web

app = Flask(__name__)  # ★ 반드시 가장 먼저 선언


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # request.form으로 받은 값은 문자열입니다.
        start = request.form["start"]
        end = request.form["end"]

        # 'coolway.runner' 모듈과 'run_from_web' 함수가 존재하고 정상적으로 동작한다고 가정합니다.
        run_from_web(start, end)

        return redirect(url_for('result'))

    # GET 요청 시 index.html 템플릿을 렌더링
    return render_template("index.html")


# ----------------- 오류 수정 부분 -----------------

@app.route("/result")
def result():  # 'def result:'를 'def result():'로 수정했습니다.
    return render_template("result.html")


# -----------------------------------------------

if __name__ == "__main__":
    # 포트 충돌 등의 문제가 없다면, debug=True로 개발 시 편리합니다.
    app.run(debug=True)