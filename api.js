/**
 * api.js — ADJ Technologies Website API Layer
 * ─────────────────────────────────────────────
 * Central module for all backend communication.
 * Import or include this file before any page script that needs API calls.
 *
 * Backend base URL: update BASE_URL to point at your Flask / server host.
 * For local development set:  http://127.0.0.1:5000
 * For production set:         https://yourdomain.com  (or leave as '' for same-origin)
 */

const ADJ_API = (() => {
  /* ─── CONFIG ─────────────────────────────────────────────────────────── */
  const BASE_URL = '';          // e.g. 'https://api.adjtech.in' or '' for same-origin
  const DEFAULT_TIMEOUT_MS = 10000;   // 10 s hard timeout per request

  /* ─── ENDPOINTS ──────────────────────────────────────────────────────── */
  const ENDPOINTS = {
    contactSubmit:  '/api/contact',       // POST  — contact form submission
    careerNotify:   '/api/career-notify', // POST  — "notify me when hiring" form
    services:       '/api/services',      // GET   — fetch service list (future use)
    healthCheck:    '/api/health',        // GET   — server health ping
  };

  /* ─── HELPERS ────────────────────────────────────────────────────────── */

  /**
   * fetchWithTimeout — wrapper around fetch() that rejects after `ms` milliseconds.
   * @param {string} url
   * @param {RequestInit} options
   * @param {number} [ms]
   * @returns {Promise<Response>}
   */
  async function fetchWithTimeout(url, options = {}, ms = DEFAULT_TIMEOUT_MS) {
    const controller = new AbortController();
    const timerId = setTimeout(() => controller.abort(), ms);
    try {
      const response = await fetch(url, { ...options, signal: controller.signal });
      return response;
    } finally {
      clearTimeout(timerId);
    }
  }

  /**
   * buildURL — joins BASE_URL with an endpoint path.
   * @param {string} path
   * @returns {string}
   */
  function buildURL(path) {
    return `${BASE_URL}${path}`;
  }

  /**
   * handleResponse — parse JSON and surface API-level errors.
   * Expects backend to return { success: bool, message: string, data?: any }
   * @param {Response} response
   * @returns {Promise<object>}
   */
  async function handleResponse(response) {
    let body;
    try {
      body = await response.json();
    } catch {
      throw new Error(`Server returned non-JSON response (HTTP ${response.status})`);
    }
    if (!response.ok) {
      throw new Error(body.message || `HTTP error ${response.status}`);
    }
    return body;
  }

  /* ─── PUBLIC API ─────────────────────────────────────────────────────── */

  /**
   * submitContact — sends the contact form data to the backend.
   *
   * Expected payload fields:
   *   name, email, mobile, country_code, service, subject, message
   *
   * @param {Object|FormData} payload  — plain object or FormData instance
   * @returns {Promise<{ success: boolean, message: string }>}
   *
   * Usage:
   *   const result = await ADJ_API.submitContact({ name: 'Aneesh', ... });
   */
  async function submitContact(payload) {
    const isFormData = payload instanceof FormData;
    const options = {
      method: 'POST',
      body: isFormData ? payload : JSON.stringify(payload),
    };
    if (!isFormData) {
      options.headers = { 'Content-Type': 'application/json' };
    }

    const response = await fetchWithTimeout(buildURL(ENDPOINTS.contactSubmit), options);
    return handleResponse(response);
  }

  /**
   * submitCareerNotify — registers a candidate for job notifications.
   *
   * Expected payload fields:
   *   name, email, phone (optional), role
   *
   * @param {Object} payload
   * @returns {Promise<{ success: boolean, message: string }>}
   *
   * Usage:
   *   const result = await ADJ_API.submitCareerNotify({ name: 'Aneesh', email: '...', role: 'Data Analyst' });
   */
  async function submitCareerNotify(payload) {
    const response = await fetchWithTimeout(buildURL(ENDPOINTS.careerNotify), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse(response);
  }

  /**
   * getServices — fetches the list of services from the backend (future use).
   *
   * @returns {Promise<{ success: boolean, data: Array }>}
   *
   * Usage:
   *   const { data } = await ADJ_API.getServices();
   */
  async function getServices() {
    const response = await fetchWithTimeout(buildURL(ENDPOINTS.services), {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    return handleResponse(response);
  }

  /**
   * healthCheck — pings the backend to verify connectivity.
   *
   * @returns {Promise<{ success: boolean, status: string }>}
   *
   * Usage:
   *   const { status } = await ADJ_API.healthCheck();
   */
  async function healthCheck() {
    const response = await fetchWithTimeout(buildURL(ENDPOINTS.healthCheck), {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    return handleResponse(response);
  }

  /* ─── EXPORTS ────────────────────────────────────────────────────────── */
  return {
    submitContact,
    submitCareerNotify,
    getServices,
    healthCheck,
    // expose for advanced usage / extension
    ENDPOINTS,
    BASE_URL,
  };
})();

/* ─── PAGE-LEVEL INTEGRATION ──────────────────────────────────────────────
 *
 * Contact Form  (contact.html)
 * ─────────────────────────────
 * The contact form in contact.html already calls  submitForm(event).
 * Replace or extend that function to use ADJ_API:
 *
 *   async function submitForm(e) {
 *     e.preventDefault();
 *     const btn = document.getElementById('submitBtn');
 *     btn.disabled = true;
 *     btn.textContent = 'Sending…';
 *     const form = document.getElementById('contactForm');
 *     const data = Object.fromEntries(new FormData(form));
 *     try {
 *       await ADJ_API.submitContact(data);
 *       document.getElementById('formSuccess').style.display = 'block';
 *       btn.textContent = 'Sent ✓';
 *       form.reset();
 *     } catch (err) {
 *       btn.textContent = 'Retry';
 *       btn.disabled = false;
 *       alert('Could not send message. Please try again or email us directly.');
 *       console.error('[ADJ API] contact error:', err);
 *     }
 *   }
 *
 *
 * Career Notify Form  (career.html)
 * ────────────────────────────────
 *   async function submitNotify() {
 *     const name  = document.getElementById('notifyName').value.trim();
 *     const email = document.getElementById('notifyEmail').value.trim();
 *     const phone = document.getElementById('notifyPhone').value.trim();
 *     const role  = document.getElementById('notifyRole').value;
 *     if (!name || !email) { alert('Please enter your name and email.'); return; }
 *     try {
 *       await ADJ_API.submitCareerNotify({ name, email, phone, role });
 *       document.getElementById('notifySuccess').style.display = 'block';
 *     } catch (err) {
 *       alert('Could not register. Please try again.');
 *       console.error('[ADJ API] career-notify error:', err);
 *     }
 *   }
 *
 ──────────────────────────────────────────────────────────────────────── */
