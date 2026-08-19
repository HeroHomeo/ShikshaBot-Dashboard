/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║                                                                  ║
 * ║   ░█▀▀░█▀█░█▀▄░█▀▀░█░█   ░█▀▄░█▀▀░█░█░█▀▀                     ║
 * ║   ░█░░░█░█░█░█░█▀▀░▄▀▄   ░█░█░█▀▀░▀▄▀░▀▀█                     ║
 * ║   ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀░▀   ░▀▀░░▀▀▀░░▀░░▀▀▀                     ║
 * ║                                                                  ║
 * ║           © 2026 Avinash aka Shroud.bean — All Rights Reserved    ║
 * ║                                                                  ║
    * ║                                                                  ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

"use client";

import React, { useState } from "react";
import { 
  Zap,
  Type,
  Link as LinkIcon,
  MessageSquare,
  UserMinus,
  ShieldAlert,
  Gavel,
  RefreshCcw,
  Save
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Select } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { AutomodConfig } from "@/types/api";

const PUNISHMENT_OPTIONS = [
  { value: "delete", label: "Delete Message" },
  { value: "warn", label: "Warn User" },
  { value: "mute", label: "Mute User" },
  { value: "kick", label: "Kick User" },
  { value: "ban", label: "Ban User" },
];

const RULES = [
  { id: 'anti_spam', name: 'Anti Spam', desc: 'Detects and removes repetitive messages or rapid firing.', icon: Zap },
  { id: 'anti_caps', name: 'Anti Caps', desc: 'Prevents excessive use of uppercase letters.', icon: Type },
  { id: 'anti_links', name: 'Anti Links', desc: 'Blocks unauthorized external links in channels.', icon: LinkIcon },
  { id: 'anti_invites', name: 'Anti Invites', desc: 'Automatically removes Discord server invite links.', icon: MessageSquare },
  { id: 'anti_mentions', name: 'Anti Mass Mention', desc: 'Protects against mentioned spam (@everyone, @here).', icon: UserMinus },
];

interface AutomodFormProps {
  initialConfig: AutomodConfig;
  guildId: string;
}

export function AutomodForm({ initialConfig, guildId }: AutomodFormProps) {
  const [config, setConfig] = useState<AutomodConfig>(initialConfig);
  const [saving, setSaving] = useState(false);
  const [newWord, setNewWord] = useState("");
  const [blacklistWords, setBlacklistWords] = useState<string[]>(initialConfig.blacklist_words || []);

  const handleToggle = (key: string) => {
    setConfig({
      ...config,
      enabled: key === 'master' ? !config.enabled : config.enabled,
    });
  };

  const handlePunishmentChange = (ruleId: string, value: string) => {
    const newPunishments = { ...config.punishments };
    newPunishments[ruleId] = value;
    setConfig({ ...config, punishments: newPunishments });
  };

  const handleSave = async () => {
    setSaving(true);

    const promise = api.updateAutomod(guildId, {
      enabled: config.enabled,
      punishments: config.punishments,
      blacklist_words: blacklistWords,
    });

    toast.promise(promise, {
      loading: 'Saving configuration...',
      success: 'Configuration saved successfully!',
      error: (err) => err.message || 'Failed to update settings',
    });

    try {
      await promise;
    } catch (err: any) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
      <div className="lg:col-span-3 space-y-6">
        <div className="bg-[#141B2D] border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="p-8 space-y-6">
            <div className="flex items-center justify-between mb-4">
               <h3 className="text-sm font-black uppercase text-slate-500 tracking-widest">Master Control</h3>
               <Switch 
                  checked={config.enabled} 
                  onCheckedChange={() => handleToggle('master')}
               />
            </div>

            <div className="space-y-4">
              {RULES.map((rule) => {
                const isEnabled = config.enabled && config.punishments?.[rule.id] !== undefined;
                return (
                  <div 
                    key={rule.id}
                    className={cn(
                      "p-6 rounded-2xl border transition-all duration-300",
                      config.enabled ? "bg-slate-900/40 border-slate-800" : "bg-slate-900/10 border-slate-900 opacity-40 grayscale"
                    )}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                      <div className="flex items-center gap-4">
                        <div className={cn(
                          "h-12 w-12 rounded-xl flex items-center justify-center transition-colors",
                          isEnabled ? "bg-primary/20 text-primary" : "bg-slate-800 text-slate-500"
                        )}>
                          <rule.icon className="h-6 w-6" />
                        </div>
                        <div>
                          <h3 className="font-bold text-white">{rule.name}</h3>
                          <p className="text-xs text-slate-500 max-w-xs">{rule.desc}</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-4">
                         {isEnabled && (
                           <div className="flex items-center gap-2 animate-in fade-in slide-in-from-right-2 duration-300">
                             <Gavel className="h-4 w-4 text-primary" />
                             <Select 
                               value={config.punishments[rule.id] || "delete"}
                               onValueChange={(val) => handlePunishmentChange(rule.id, val)}
                               options={PUNISHMENT_OPTIONS}
                               className="w-40"
                             />
                           </div>
                         )}
                         <div className="h-8 w-[1px] bg-slate-800 hidden sm:block" />
                         <Switch 
                          disabled={!config.enabled}
                          checked={config.punishments?.[rule.id] !== undefined}
                          onCheckedChange={() => {
                            const newPunishments = { ...config.punishments };
                            if (newPunishments[rule.id]) {
                              delete newPunishments[rule.id];
                            } else {
                              newPunishments[rule.id] = "delete";
                            }
                            setConfig({...config, punishments: newPunishments});
                          }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="mt-8 pt-8 border-t border-slate-800/60 space-y-4">
              <div className="flex items-center gap-2 mb-2">
                <ShieldAlert className="h-5 w-5 text-red-500" />
                <h3 className="font-bold text-white">Blacklisted Words (Profanity Filter)</h3>
              </div>
              <p className="text-sm text-slate-400">
                Any message containing these words will be automatically deleted.
              </p>
              
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newWord}
                  onChange={(e) => setNewWord(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      if (newWord.trim() && !blacklistWords.includes(newWord.trim().toLowerCase())) {
                        setBlacklistWords([...blacklistWords, newWord.trim().toLowerCase()]);
                        setNewWord("");
                      }
                    }
                  }}
                  placeholder="Enter a word to block..."
                  className="flex h-10 w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-slate-950"
                />
                <Button
                  onClick={(e) => {
                    e.preventDefault();
                    if (newWord.trim() && !blacklistWords.includes(newWord.trim().toLowerCase())) {
                      setBlacklistWords([...blacklistWords, newWord.trim().toLowerCase()]);
                      setNewWord("");
                    }
                  }}
                  type="button"
                >
                  Add
                </Button>
              </div>

              {blacklistWords.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-4 p-4 bg-slate-900/50 rounded-xl border border-slate-800">
                  {blacklistWords.map((word) => (
                    <span 
                      key={word} 
                      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-500/10 text-red-500 text-sm border border-red-500/20"
                    >
                      {word}
                      <button 
                        onClick={(e) => {
                          e.preventDefault();
                          setBlacklistWords(blacklistWords.filter((w) => w !== word));
                        }}
                        className="hover:text-red-400 transition-colors"
                        type="button"
                      >
                        &times;
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            <Button 
              onClick={handleSave}
              disabled={saving}
              className="w-full h-14 text-base font-bold gap-2"
            >
              {saving ? <RefreshCcw className="h-5 w-5 animate-spin" /> : <Save className="h-5 w-5" />}
              Save Moderation Rules
            </Button>
          </div>
        </div>
      </div>

      <div className="space-y-6">
         <div className="bg-[#141B2D] border border-slate-800 rounded-3xl p-6">
            <h3 className="text-sm font-black uppercase text-slate-500 tracking-widest mb-4">Logging Level</h3>
            <div className="space-y-3">
               <div className="p-3 bg-slate-900/50 rounded-xl border border-white/5 flex items-center justify-between">
                  <span className="text-sm text-slate-400">Log Channel</span>
                  <span className="text-xs font-mono text-primary">#{config.logging_channel || 'None'}</span>
               </div>
               <p className="text-[10px] text-slate-500 italic text-center">Mod logs are automatically sent to the configured channel.</p>
            </div>
         </div>

         <div className="bg-gradient-to-br from-primary/10 to-transparent border border-primary/20 rounded-3xl p-6 relative overflow-hidden group">
            <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:scale-110 transition-transform">
              <ShieldAlert className="h-32 w-32 text-white" />
            </div>
            <h3 className="text-sm font-bold text-white mb-2">Automod AI</h3>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">Our neural network analyzes message context to prevent false positives.</p>
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-primary" />
              <span className="text-[10px] font-black uppercase text-primary">V2 Active</span>
            </div>
         </div>
      </div>
    </div>
  );
}
