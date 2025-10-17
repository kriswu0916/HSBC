# main.py
import ast
import json

# ----------------------------------------------------------------------------
# 模块一: 代码摄取 (Code Ingestion)
# ----------------------------------------------------------------------------
# 在实际项目中，这部分会从Git仓库读取文件。此处为简化，直接使用字符串。
SOURCE_CODE_EXAMPLE = """
class UserService:
    \"\"\"
    一个处理用户相关业务逻辑的服务。
    负责用户的创建、查询和删除。
    依赖 UserRepository 来进行数据库操作。
    \"\"\"
    def __init__(self, db_session):
        self.user_repository = UserRepository(db_session)

    def create_user(self, username: str, email: str, age: int) -> dict:
        \"\"\"
        创建一个新用户并将其保存到数据库。

        在创建用户之前，会首先检查用户名或邮箱是否已存在。
        如果存在，则会抛出 ValueError 异常。
        成功创建后，返回用户信息字典，但不包含密码。
        \"\"\"
        if self.user_repository.find_by_username(username):
            raise ValueError(f"Username {username} already exists.")
        if self.user_repository.find_by_email(email):
            raise ValueError(f"Email {email} already exists.")
        
        # 假设 User 和 UserRepository 已经定义
        # new_user = User(username=username, email=email, age=age)
        # saved_user = self.user_repository.save(new_user)
        
        # return {
        #     "id": saved_user.id,
        #     "username": saved_user.username,
        #     "email": saved_user.email
        # }
        print(f"User {username} created successfully.")
        return {"id": 1, "username": username, "email": email}

"""

# ----------------------------------------------------------------------------
# 模块二: 静态分析与知识提取 (Static Analysis & Knowledge Extraction)
# ----------------------------------------------------------------------------
def analyze_python_code(source_code: str, file_path: str) -> dict:
    """
    使用 Python 内置的 ast 模块解析代码，提取关键信息。
    这是构建代码知识图谱的第一步。
    """
    tree = ast.parse(source_code)
    analysis_result = {"file_path": file_path, "entities": []}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_info = {
                "type": "class", "name": node.name,
                "docstring": ast.get_docstring(node), "methods": []
            }
            for method_node in node.body:
                if isinstance(method_node, ast.FunctionDef):
                    method_info = {
                        "type": "method", "name": method_node.name,
                        "args": [arg.arg for arg in method_node.args.args],
                        "docstring": ast.get_docstring(method_node),
                        "line_start": method_node.lineno
                    }
                    class_info["methods"].append(method_info)
            analysis_result["entities"].append(class_info)
    return analysis_result

# ----------------------------------------------------------------------------
# 模块三: 智能生成引擎 (Intelligent Generation Engine)
# ----------------------------------------------------------------------------
def generate_prompt_for_qa(analysis: dict, target_method: str) -> str:
    """基于代码分析结果，为LLM生成一个高质量的Prompt。"""
    method_info = None
    for entity in analysis.get("entities", []):
        if entity["type"] == "class":
            for method in entity["methods"]:
                if method["name"] == target_method:
                    method_info = method
                    break
    if not method_info: return "错误：未找到目标方法。"

    prompt = f"""
    请根据下面提供的代码上下文，生成一个关于核心业务流程的问答（QA）对。

    **代码上下文:**
    - 文件路径: {analysis['file_path']}
    - 目标方法: {method_info['name']}
    - 方法的说明文档: {method_info['docstring']}

    **你的任务:**
    1.  设计一个从用户角度出发的 **问题 (question)**。
    2.  根据代码逻辑和文档，撰写一个详细、准确的 **答案 (answer)**。
    3.  以我指定的JSON格式输出，并包含 `trace` 信息，指明答案的依据。
    """
    return prompt.strip()

def generate_training_data_mock(prompt: str) -> str:
    """
    **模拟函数**: 模拟对 Qwen 2.5 大模型的API调用。
    在真实场景中，这里会是网络请求和响应处理。
    """
    print("--- [INFO] Prompt 发送给 LLM ---")
    print(prompt)
    print("---------------------------------")
    
    mock_response = {
      "id": "qa_user_creation_001",
      "scenario": "business_logic_qa",
      "source_repository": "internal_project/user_management_system",
      "metadata": { "language": "Python", "domain": "User Management" },
      "question": "在用户管理系统中，创建一个新用户的完整业务流程是怎样的？有哪些前置校验？",
      "answer": {
        "summary": "创建一个新用户需调用`UserService`的`create_user`方法。流程首先会校验用户名和邮箱的唯一性，防止重复。校验通过后，系统会创建用户实体并持久化到数据库，最后返回新用户的基本信息（ID、用户名等）。",
        "trace": [{
            "type": "entrypoint",
            "description": "The primary business logic for creating a new user.",
            "file_path": "services/user_service.py",
            "class": "UserService",
            "method": "create_user",
            "line_start": 15
        }]
      }
    }
    return json.dumps(mock_response, indent=2, ensure_ascii=False)

# ----------------------------------------------------------------------------
# 主执行流程 (Main Execution Flow)
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    print("[1/3] 开始分析源代码...")
    analyzed_data = analyze_python_code(SOURCE_CODE_EXAMPLE, "services/user_service.py")
    
    print("[2/3] 为 'create_user' 方法生成 Prompt...")
    prompt_for_llm = generate_prompt_for_qa(analyzed_data, target_method="create_user")
    
    print("[3/3] (模拟)调用LLM生成训练数据...")
    final_training_data_json = generate_training_data_mock(prompt_for_llm)
    
    print("\n✅ 成功生成一份高质量的训练数据：\n")
    print(final_training_data_json)