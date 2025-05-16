#include <windows.h>
#include <commctrl.h>
#include <string>

#define ID_EDITOR 100
#define ID_RUN_BTN 101
#define ID_OUTPUT 102

LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);

int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, PWSTR pCmdLine, int nCmdShow) {
    // Register window class
    WNDCLASSW wc = {0};
    wc.lpfnWndProc = WindowProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = L"ShayIDEClass";
    RegisterClassW(&wc);

    // Create main window
    HWND hwnd = CreateWindowExW(
        0,
        L"ShayIDEClass",
        L"Shai Language IDE",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, 800, 600,
        NULL, NULL, hInstance, NULL
    );

    if (hwnd == NULL) {
        return 0;
    }

    // Create controls
    CreateWindowW(L"EDIT", L"", 
        WS_CHILD | WS_VISIBLE | WS_VSCROLL | ES_MULTILINE | ES_AUTOVSCROLL,
        10, 10, 780, 300, hwnd, (HMENU)ID_EDITOR, hInstance, NULL);

    CreateWindowW(L"BUTTON", L"Run (نفذ)", 
        WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
        10, 320, 100, 30, hwnd, (HMENU)ID_RUN_BTN, hInstance, NULL);

    CreateWindowW(L"EDIT", L"", 
        WS_CHILD | WS_VISIBLE | WS_VSCROLL | ES_MULTILINE | ES_AUTOVSCROLL | ES_READONLY,
        10, 360, 780, 200, hwnd, (HMENU)ID_OUTPUT, hInstance, NULL);

    ShowWindow(hwnd, nCmdShow);

    // Message loop
    MSG msg = {0};
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return 0;
}

LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    switch (uMsg) {
        case WM_COMMAND: {
            if (LOWORD(wParam) == ID_RUN_BTN) {
                // Get code from editor
                HWND hEditor = GetDlgItem(hwnd, ID_EDITOR);
                int len = GetWindowTextLengthW(hEditor) + 1;
                wchar_t* code = new wchar_t[len];
                GetWindowTextW(hEditor, code, len);

                // TODO: Execute Shai code here
                std::wstring output = L"Executing Shai code...\n";
                output += code;

                // Display output
                HWND hOutput = GetDlgItem(hwnd, ID_OUTPUT);
                SetWindowTextW(hOutput, output.c_str());

                delete[] code;
            }
            break;
        }
        case WM_DESTROY: {
            PostQuitMessage(0);
            break;
        }
        default:
            return DefWindowProc(hwnd, uMsg, wParam, lParam);
    }
    return 0;
}
