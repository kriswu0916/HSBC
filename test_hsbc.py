'''
Author: Kris_wu
'''
# test_main.py
import pytest
from hsbc import analyze_python_code, generate_prompt_for_qa, SOURCE_CODE_EXAMPLE

# ============================================================================
# 测试用例 1: 针对代码解析模块 (analyze_python_code)
# ============================================================================

def test_analyze_python_code_normal_case():
    """
    用例 1.1 (正常情况): 测试能否正确解析一个有效的Python代码文件。
    """
    file_path = "services/user_service.py"
    analysis = analyze_python_code(SOURCE_CODE_EXAMPLE, file_path)

    # 断言基本结构正确
    assert analysis["file_path"] == file_path
    assert isinstance(analysis["entities"], list)
    assert len(analysis["entities"]) == 1

    # 断言类信息正确
    class_info = analysis["entities"][0]
    assert class_info["type"] == "class"
    assert class_info["name"] == "UserService"
    assert "处理用户相关业务逻辑的服务" in class_info["docstring"]
    assert len(class_info["methods"]) == 2 # __init__ 和 create_user

    # 断言方法信息正确
    create_user_method = next((m for m in class_info["methods"] if m["name"] == "create_user"), None)
    assert create_user_method is not None
    assert create_user_method["type"] == "method"
    assert "username" in create_user_method["args"]
    assert "创建一个新用户并将其保存到数据库" in create_user_method["docstring"]


def test_analyze_python_code_empty_file():
    """
    用例 1.2 (空文件): 测试输入为空字符串时能否正常处理。
    """
    analysis = analyze_python_code("", "empty.py")
    assert analysis["file_path"] == "empty.py"
    assert len(analysis["entities"]) == 0


def test_analyze_python_code_syntax_error():
    """
    用例 1.3 (语法错误): 测试输入包含语法错误时能否按预期抛出异常。
    """
    invalid_code = "class InvalidClass: def func("
    with pytest.raises(SyntaxError):
        analyze_python_code(invalid_code, "invalid.py")

# ============================================================================
# 测试用例 2: 针对Prompt生成模块 (generate_prompt_for_qa)
# ============================================================================

# 使用 pytest fixture 来避免重复计算分析结果
@pytest.fixture
def analysis_data():
    """提供一个预先分析好的代码数据，供后续测试使用。"""
    return analyze_python_code(SOURCE_CODE_EXAMPLE, "services/user_service.py")


def test_generate_prompt_for_qa_success(analysis_data):
    """
    用例 2.1 (方法存在): 测试当目标方法存在时，能否生成包含关键信息的Prompt。
    """
    prompt = generate_prompt_for_qa(analysis_data, "create_user")
    
    # 断言Prompt是字符串并且包含关键信息
    assert isinstance(prompt, str)
    assert "services/user_service.py" in prompt
    assert "create_user" in prompt
    assert "创建一个新用户并将其保存到数据库" in prompt # 检查是否包含了文档字符串
    assert "你的任务:" in prompt


def test_generate_prompt_for_qa_method_not_found(analysis_data):
    """
    用例 2.2 (方法不存在): 测试当目标方法不存在时，能否返回预期的错误信息。
    """
    prompt = generate_prompt_for_qa(analysis_data, "non_existent_method")
    assert "错误：未找到目标方法" in prompt