## Marflow-Software
# SmartCut - for Adobe Premiere Pro

- Version: 0.9.1
- Developer: Halatschek Wolfram
- Date: May, 2024

---

*Note:* This Extension for Adobe Premiere Pro (Software) is developed until v1.0 as part of a Bachelor-Thesis by the Developer in 2023 - 2024 at the *University of Applied Science, FH Joanneum* in *Kapfenberg, Austria*

---

This Extension analyses an audio-track from the current active Sequence in Adobe Premiere Pro and places Markers where Onsets events occur. These markers then can be used to automatically cut and align video-clips accordingly

Please be aware that it works having 1 video clip more than Onset Markers (use *Sequence info* - button within the extension).


### Install instructions

Install the Extension by executing the setup-File (Administrator privilages necessary)

After installing the extension, please set the following Registry Key accordingly:

- **Registry Path:** Computer\HKEY_CURRENT_USER\SOFTWARE\ADOBE\CSXS.11
- **Value Name:** PlayerDebugMode
- **Type:** String Value (REG_SZ)
- **Value** 1



