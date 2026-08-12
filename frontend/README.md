# Secret Santa Frontend ⚛️🎁

Single Page Application (SPA) built with **React**, powered by **Vite**, and managed using **`pnpm`**.

---

## 🎨 UI Features

* **Festive Christmas Aesthetic:** Gold, emerald green, and festive red gradients with **Glassmorphic Cards**.
* **Historical Exclusion Manager:** Interactive tag multi-select component enabling each user to select family members they **already gifted to in previous years**.
* **Result Confidentiality:** The UI only displays the registered members list; secret assignments are 100% confidential and dispatched directly via AWS SES email.
* **1-Click Share Link:** Copy group URL (`/#g-xxxx`) to share with family via messaging apps or email.

---

## 🧩 Key Components

* `src/App.jsx`: Main state control, group hash detection, and conditional view rendering.
* `src/components/Navbar.jsx`: Festive header with group creation modal trigger and link copy button.
* `src/components/CreateGroupModal.jsx`: Modal to create a new group with email and admin PIN.
* `src/components/RegisterModal.jsx`: Participant signup modal with exclusions tag selector.
* `src/components/AdminDrawModal.jsx`: Organizer confirmation modal to lock the group and dispatch SES emails.
* `src/services/api.js`: Fetch HTTP API client interfacing with AWS API Gateway / FastAPI.

---

## 💻 `pnpm` Commands

```bash
# Install dependencies
pnpm install

# Start local dev server
pnpm dev

# Build for production (output generated in dist/)
pnpm run build

# Preview production build locally
pnpm preview
```

---

## 🌐 Environment Variables Configuration

Create a `.env.local` file to override the API endpoint URL:

```env
VITE_API_URL=https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/api/v1
```
