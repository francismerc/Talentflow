import { PageHeader } from "@/components/ui/page-header";
import { SettingsPanels } from "@/components/settings/settings-panels";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Settings" description="Manage your profile, integrations, AI behavior, and workspace preferences." />
      <SettingsPanels />
    </div>
  );
}
