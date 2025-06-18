"use client";

import { useEffect } from "react";
import { TenantProvider } from "@/context/tenant_context";
import axios from "axios";


export default function ClientAuthWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    const handleAuth = async () => {
      try {
        const currentUrl = window.location.href;
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get("token");
        const tenant_slug = urlParams.get("tenant_slug");
        const app_id = urlParams.get("app_id");
        const default_url = urlParams.get("default_url");

        // If token exists in URL, it means we just logged in.
        if (token) {
          localStorage.setItem("token", token);
          localStorage.setItem("tenant_slug", tenant_slug || "");
          localStorage.setItem("app_id", app_id || "");
          localStorage.setItem("default_url", default_url || "");

          // Create a new URL object to handle query parameters properly
          const newUrl = new URL(window.location.href);

          // Remove the token parameter
          newUrl.searchParams.delete("token");

          // If there are no query parameters left, remove the '?' from the URL
          let cleanUrl = newUrl.toString();
          if (cleanUrl.endsWith("?")) {
            cleanUrl = cleanUrl.slice(0, -1);
          }

          // Update the URL without reloading the page
          window.history.replaceState({}, document.title, cleanUrl);
          return;
        }

        const storedToken = localStorage.getItem("token");
        const storedTenantSlug = localStorage.getItem("tenant_slug");
        const hasCheckedTenant = sessionStorage.getItem("hasCheckedTenant");

        // If we've already checked or user has a token and tenant, skip the call
        if (storedToken && storedTenantSlug && hasCheckedTenant === "true") {
          return;
        }

        // ⚠️ Set this before the API call to prevent re-entry even if redirect fails
        sessionStorage.setItem("hasCheckedTenant", "true");
        // console.log("NEXT_PUBLIC_TENANT_CHECK_API", process.env.NEXT_PUBLIC_TENANT_CHECK_API);
        const { data: tenantData } = await axios.post(
          `${process.env.NEXT_PUBLIC_TENANT_CHECK_API}/platform-admin/subscription/check-tenant-exist/`,
          {
            application_url: currentUrl,
          }
        );

        console.log("Tenant check response:", tenantData);

        if (tenantData?.redirect_to_iam) {
          // ⚠️ Return early after redirect to avoid continuing execution
          window.location.href = tenantData.redirect_to_iam;
          return;
        }
      } catch (error) {
        console.error("Error in auth flow:", error);
        if (
          axios.isAxiosError(error) &&
          [401, 403].includes(error.response?.status || 0)
        ) {
          localStorage.removeItem("token");
          sessionStorage.removeItem("hasCheckedTenant");
          window.location.reload();
        }
      }
    };

    if (typeof window !== "undefined") {
      handleAuth();
    }

    return () => {
      if (typeof window !== "undefined") {
        sessionStorage.removeItem("reloadCount");
      }
    };
  }, []);

  return <TenantProvider>{children}</TenantProvider>;
}
