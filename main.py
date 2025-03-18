from flask import Flask, render_template, request, redirect, url_for, session, flash
from replit import db

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Thay bằng chuỗi bí mật của bạn

# Nếu trong DB chưa có người dùng, khởi tạo dữ liệu mẫu
if "users" not in db.keys():
    db["users"] = {
        "admin": {
            "password": "1234",
            "role": "admin"
        },
        "user1": {
            "password": "pass1",
            "role": "user"
        }
    }


# Endpoint trang đăng nhập (các endpoint khác cũng cần định nghĩa nếu có)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = db["users"]
        if username in users and users[username]["password"] == password:
            session["username"] = username
            session["role"] = users[username]["role"]
            if users[username]["role"] == "admin":
                return redirect(url_for("admin"))
            else:
                return redirect(url_for("dashboard"))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không đúng!", "error")
    return render_template("login.html")


# Trang dashboard dành cho người dùng (user)


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "username" not in session or session.get("role") != "user":
        flash("Bạn không có quyền truy cập trang này.", "error")
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])


# Trang quản trị dành cho admin
@app.route("/admin")
def admin():
    if "username" not in session or session.get("role") != "admin":
        flash("Bạn không có quyền truy cập trang này.", "error")
        return redirect(url_for("login"))
    users = db["users"]
    return render_template("admin.html",
                           username=session["username"],
                           users=users)


# Endpoint edit user hoàn chỉnh
@app.route("/admin/edit/<username>", methods=["GET", "POST"])
def edit_user(username):
    # Chỉ cho phép admin truy cập
    if "username" not in session or session.get("role") != "admin":
        flash("Bạn không có quyền truy cập trang này.", "error")
        return redirect(url_for("dashboard"))

    users = db["users"]
    # Kiểm tra user tồn tại
    if username not in users:
        flash("User không tồn tại.", "error")
        return redirect(url_for("admin"))

    if request.method == "POST":
        new_password = request.form["password"]
        new_role = request.form["role"]
        users[username] = {"password": new_password, "role": new_role}
        db["users"] = users
        flash("User được cập nhật thành công!", "success")
        return redirect(url_for("admin"))

    # GET: render trang sửa user với thông tin hiện tại
    return render_template("edit_user.html",
                           username=username,
                           user=users[username])


@app.route("/admin/add", methods=["GET", "POST"])
def add_user():
    if "username" not in session or session.get("role") != "admin":
        flash("Bạn không có quyền truy cập.", "error")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        new_username = request.form["username"]
        new_password = request.form["password"]
        new_role = request.form["role"]
        users = db["users"]
        if new_username in users:
            flash("User đã tồn tại.", "error")
        else:
            users[new_username] = {"password": new_password, "role": new_role}
            db["users"] = users
            flash("User được thêm thành công!", "success")
            return redirect(url_for("admin"))
    return render_template("add_user.html")


@app.route("/admin/delete/<username>")
def delete_user(username):
    # Kiểm tra đăng nhập và quyền admin
    if "username" not in session or session.get("role") != "admin":
        flash("Bạn không có quyền truy cập trang này.", "error")
        return redirect(url_for("dashboard"))

    users = db["users"]
    # Kiểm tra xem user có tồn tại hay không
    if username in users:
        del users[username]
        db["users"] = users
        flash("User đã được xóa thành công!", "success")
    else:
        flash("User không tồn tại.", "error")

    return redirect(url_for("admin"))


# Đăng xuất
@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("role", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
