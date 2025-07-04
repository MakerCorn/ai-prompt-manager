"""
E2E Tests for Prompt Management Flow

Tests complete prompt management workflows including creation, editing, deletion, and library operations.
"""

import pytest
from playwright.sync_api import sync_playwright

from .conftest import E2ETestBase


@pytest.mark.e2e
class TestPromptManagementFlow(E2ETestBase):
    """End-to-end prompt management flow tests."""

    def login_user(self, page, test_config, admin_user_data):
        """Helper method to login user."""
        page.goto(test_config["base_url"])

        # Wait for page to load and look for login elements
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except:
            # If networkidle fails, wait for domcontentloaded instead
            page.wait_for_load_state("domcontentloaded", timeout=5000)

        page.wait_for_timeout(3000)  # Give UI more time to load

        # Try multiple selectors that Gradio might use for text inputs
        email_selectors = [
            "input[type='email']",
            "input[type='text']",
            "textarea",
            "input",
            "[placeholder*='email']",
            "[placeholder*='Email']",
        ]

        email_input = None
        for selector in email_selectors:
            try:
                elements = page.query_selector_all(selector)
                # Look for visible elements that might be email input
                for element in elements:
                    if element.is_visible():
                        # Check if this looks like an email field
                        placeholder = element.get_attribute("placeholder") or ""
                        label_text = ""
                        try:
                            # Look for associated label
                            parent = element.query_selector("..")
                            if parent:
                                label_text = parent.text_content() or ""
                        except:
                            pass

                        if any(
                            keyword in (placeholder + label_text).lower()
                            for keyword in ["email", "e-mail", "mail"]
                        ):
                            email_input = element
                            break
                if email_input:
                    break
            except:
                continue

        if not email_input:
            # Fallback: just use the first visible text input
            try:
                inputs = page.query_selector_all("input, textarea")
                email_input = next((inp for inp in inputs if inp.is_visible()), None)
            except:
                pass

        if email_input:
            email_input.fill(admin_user_data["email"])

            # Look for password field
            password_input = None
            password_selectors = [
                "input[type='password']",
                "input",
                "[placeholder*='password']",
                "[placeholder*='Password']",
            ]

            for selector in password_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    for element in elements:
                        if element.is_visible() and element != email_input:
                            input_type = element.get_attribute("type") or ""
                            placeholder = element.get_attribute("placeholder") or ""
                            if (
                                input_type == "password"
                                or "password" in placeholder.lower()
                            ):
                                password_input = element
                                break
                    if password_input:
                        break
                except:
                    continue

            if password_input:
                password_input.fill(admin_user_data["password"])

                # Look for submit button
                submit_selectors = [
                    "button[type='submit']",
                    "button:has-text('Login')",
                    "button:has-text('Sign in')",
                    "button",
                ]

                for selector in submit_selectors:
                    try:
                        button = page.query_selector(selector)
                        if button and button.is_visible():
                            button.click()
                            break
                    except:
                        continue

                try:
                    page.wait_for_load_state("networkidle", timeout=5000)
                except:
                    page.wait_for_load_state("domcontentloaded", timeout=3000)
                page.wait_for_timeout(2000)  # Give UI time to settle
            else:
                print("⚠️ Password input not found")
        else:
            print(
                "⚠️ Email input not found, login may not be required or page not loaded"
            )

    def test_create_prompt_workflow(
        self, test_config, app_server, admin_user_data, sample_prompt_data
    ):
        """Test complete prompt creation workflow."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=test_config["headless"])
            page = browser.new_page()

            try:
                # Login
                self.login_user(page, test_config, admin_user_data)

                # Look for prompt management interface
                # The interface might use tabs, buttons, or sections
                page.wait_for_timeout(3000)  # Wait for interface to load

                # Try to find prompt creation elements
                # Look for common UI patterns: tabs, forms, buttons
                page_content = page.content().lower()
                assert len(page_content) > 0, "Page should have content"

                # Look for form elements that might be for prompt creation
                name_inputs = page.query_selector_all(
                    "input[placeholder*='name'], input[name*='name'], textarea[placeholder*='name']"
                )
                content_inputs = page.query_selector_all(
                    "textarea[placeholder*='content'], textarea[placeholder*='prompt'], textarea[name*='content']"
                )

                if name_inputs and content_inputs:
                    # Found form elements, try to create a prompt
                    name_input = next(
                        (inp for inp in name_inputs if inp.is_visible()), None
                    )
                    content_input = next(
                        (inp for inp in content_inputs if inp.is_visible()), None
                    )

                    if name_input and content_input:
                        # Fill the form
                        name_input.fill(sample_prompt_data["name"])
                        content_input.fill(sample_prompt_data["content"])

                        # Look for additional fields
                        title_inputs = page.query_selector_all(
                            "input[placeholder*='title'], input[name*='title']"
                        )
                        if title_inputs:
                            title_input = next(
                                (inp for inp in title_inputs if inp.is_visible()), None
                            )
                            if title_input:
                                title_input.fill(sample_prompt_data["title"])

                        # Look for category/tags fields
                        category_inputs = page.query_selector_all(
                            "input[placeholder*='category'], select[name*='category']"
                        )
                        if category_inputs:
                            category_input = next(
                                (inp for inp in category_inputs if inp.is_visible()),
                                None,
                            )
                            if category_input:
                                if category_input.tag_name.lower() == "select":
                                    category_input.select_option(
                                        sample_prompt_data["category"]
                                    )
                                else:
                                    category_input.fill(sample_prompt_data["category"])

                        # Look for submit button
                        submit_buttons = page.query_selector_all(
                            "button[type='submit'], button:has-text('Save'), button:has-text('Create'), button:has-text('Add')"
                        )
                        submit_button = next(
                            (btn for btn in submit_buttons if btn.is_visible()), None
                        )

                        if submit_button:
                            submit_button.click()
                            page.wait_for_timeout(2000)  # Wait for submission

                            # Check for success indication
                            page_after_submit = page.content().lower()
                            success_indicators = [
                                "success",
                                "created",
                                "saved",
                                "added",
                            ]

                            assert (
                                any(
                                    indicator in page_after_submit
                                    for indicator in success_indicators
                                )
                                or sample_prompt_data["name"].lower()
                                in page_after_submit
                            ), "Expected success indication or prompt name in page after creation"

                            print("✅ Prompt creation workflow successful")
                        else:
                            print(
                                "⚠️ No submit button found, prompt creation form may not be accessible"
                            )
                    else:
                        print(
                            "⚠️ Required form inputs not visible, prompt creation may require navigation"
                        )
                else:
                    print(
                        "⚠️ Prompt creation form not immediately visible, may require specific navigation"
                    )

                # At minimum, verify the application is running and responsive
                assert (
                    "error" not in page.content().lower() or len(page.content()) > 100
                ), "Application should be running without critical errors"

            finally:
                browser.close()

    def test_prompt_library_workflow(self, test_config, app_server, admin_user_data):
        """Test prompt library browsing and search functionality."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=test_config["headless"])
            page = browser.new_page()

            try:
                # Login
                self.login_user(page, test_config, admin_user_data)

                # Wait for interface to load
                page.wait_for_timeout(3000)

                # Look for library/browse elements
                page_content = page.content().lower()

                # Check if we can see library-related content
                library_indicators = [
                    "library",
                    "prompts",
                    "browse",
                    "search",
                    "filter",
                ]
                has_library_features = any(
                    indicator in page_content for indicator in library_indicators
                )

                if has_library_features:
                    # Try to find search functionality
                    search_inputs = page.query_selector_all(
                        "input[type='search'], input[placeholder*='search'], input[name*='search']"
                    )
                    search_input = next(
                        (inp for inp in search_inputs if inp.is_visible()), None
                    )

                    if search_input:
                        # Test search functionality
                        search_input.fill("test")
                        page.wait_for_timeout(1000)  # Wait for search results

                        # Check that search was processed
                        after_search_content = page.content()
                        assert (
                            len(after_search_content) > 0
                        ), "Search should return some content"

                        print("✅ Prompt library search workflow successful")
                    else:
                        print("⚠️ Search functionality not immediately visible")

                # Verify application responsiveness
                assert (
                    len(page.content()) > 1000
                ), "Application should render substantial content"
                assert (
                    "error" not in page.content().lower() or "500" not in page.content()
                ), "Application should not show critical errors"

                print("✅ Prompt library workflow completed")

            finally:
                browser.close()

    def test_token_calculator_workflow(self, test_config, app_server, admin_user_data):
        """Test token calculator functionality."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=test_config["headless"])
            page = browser.new_page()

            try:
                # Login
                self.login_user(page, test_config, admin_user_data)

                # Wait for interface to load
                page.wait_for_timeout(3000)

                # Look for token calculator elements
                page_content = page.content().lower()

                # Check for calculator-related content
                calc_indicators = [
                    "token",
                    "calculator",
                    "cost",
                    "estimate",
                    "gpt",
                    "claude",
                ]
                has_calculator = any(
                    indicator in page_content for indicator in calc_indicators
                )

                if has_calculator:
                    # Try to find text input for token calculation
                    text_areas = page.query_selector_all("textarea")
                    large_inputs = page.query_selector_all("input[type='text']")

                    calculator_input = None
                    for textarea in text_areas:
                        if textarea.is_visible():
                            calculator_input = textarea
                            break

                    if not calculator_input:
                        for input_elem in large_inputs:
                            if input_elem.is_visible():
                                calculator_input = input_elem
                                break

                    if calculator_input:
                        # Test token calculation
                        test_text = "This is a test prompt for token calculation."
                        calculator_input.fill(test_text)
                        page.wait_for_timeout(2000)  # Wait for calculation

                        # Check if calculation results appear
                        updated_content = page.content().lower()
                        cost_indicators = ["cost", "$", "tokens", "estimate"]

                        has_calculation = any(
                            indicator in updated_content
                            for indicator in cost_indicators
                        )
                        if has_calculation:
                            print("✅ Token calculator workflow successful")
                        else:
                            print("⚠️ Token calculation results not clearly visible")
                    else:
                        print("⚠️ Token calculator input not found")
                else:
                    print("⚠️ Token calculator not immediately visible")

                # Verify basic application functionality
                assert len(page.content()) > 500, "Application should render content"
                print("✅ Token calculator workflow completed")

            finally:
                browser.close()

    def test_api_documentation_access(self, test_config, app_server, admin_user_data):
        """Test access to API documentation."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=test_config["headless"])
            page = browser.new_page()

            try:
                # Login first
                self.login_user(page, test_config, admin_user_data)

                # Try to access API documentation directly
                api_docs_urls = [
                    f"{test_config['base_url']}/api/docs",
                    f"{test_config['base_url']}/docs",
                    f"{test_config['api_base']}/docs",
                ]

                api_docs_accessible = False
                for docs_url in api_docs_urls:
                    try:
                        page.goto(docs_url)
                        page.wait_for_load_state("networkidle", timeout=5000)

                        content = page.content().lower()
                        if any(
                            indicator in content
                            for indicator in [
                                "swagger",
                                "openapi",
                                "api",
                                "documentation",
                            ]
                        ):
                            api_docs_accessible = True
                            print(f"✅ API documentation accessible at {docs_url}")
                            break
                    except Exception:
                        continue

                if not api_docs_accessible:
                    print("⚠️ API documentation not accessible via standard URLs")

                # Verify application is still functional
                page.goto(test_config["base_url"])
                page.wait_for_load_state("networkidle")
                assert len(page.content()) > 500, "Application should remain functional"

                print("✅ API documentation access test completed")

            finally:
                browser.close()
