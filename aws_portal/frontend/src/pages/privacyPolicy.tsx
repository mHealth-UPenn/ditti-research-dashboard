/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * Ditti Research Dashboard is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ditti Research Dashboard is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

export function PrivacyPolicy() {
  return (
    <div className="px-0 sm:px-16 bg-extra-light">
      <div className="px-4 sm:px-8 md:px-16 lg:px-24 xl:px-32 2xl:px-40 py-16 bg-white">
        <h3><span>Privacy Policy for the Ditti Research Dashboard</span></h3>
        <p><span>We institute strict procedures to maintain confidentiality and will adhere to the </span><span className="font-bold">2024 HIPAA Standards for Privacy of Individually Identifiable Health Information (the PrivacyRule)</span><span>. No personally identifiable information will be collected when using the Ditti ResearchDashboard. Each user will be assigned a unique User ID that contains no personal identifiers. All data isstored on </span><span className="font-bold">Amazon Web Services (AWS)</span><span>&nbsp;and is maintained by the</span><span className="font-bold">&nbsp;University of Pennsylvania</span><span>.</span></p>
        <h4 className="mt-12"><span>1. Data Request and Deletion Process</span></h4>
        <p><span>Users can request deletion of their account at any time by contacting a member of their researchteam or via the following link: </span><span><a className="link" href="https://www.google.com/url?q=https://hosting.med.upenn.edu/forms/DittiApp/view.php?id%3D10677&amp;sa=D&amp;source=editors&amp;ust=1732572983279481&amp;usg=AOvVaw3f8Wbum-A3vzDJdcnMSpSs">DataRequest Link</a></span><span>. This link is also accessible through the Ditti ResearchDashboard.</span></p>
        <p><span>De-identified data collected as part of a study approved by an accreditedInstitutional Review Board (IRB) will not be deleted according to research guidelines. Data collected for anapproved study will only be stored in an anonymized manner that cannot be linked to the user.</span></p>
        <h4 className="mt-12"><span>2. Compliance with Data Protection Laws</span></h4>
        <p><span>The Ditti Research Dashboard will be used exclusively within healthcare contexts and complieswith the </span><span className="font-bold">2024 HIPAA Standards for Privacy of Individually Identifiable HealthInformation</span><span>. It is not designed for international use or for contexts outside ofhealthcare research.</span></p>
        <h4 className="mt-12"><span>3. Security Measures</span></h4>
        <ul className="list-disc ml-6">
          <li><span>Application data within AWS is transferred securely using the </span><span className="font-bold">AWS Private Network</span><span>.</span></li>
          <li><span>Data transferred outside AWS is encrypted using </span><span className="font-bold">HTTPS/TLS protocols</span><span>.</span></li>
          <li><span>Data at rest is encrypted according to </span><span className="font-bold">AWSstandards</span><span>.</span></li>
          <li><span>Access to user data is managed using </span><span className="font-bold">AWS IAMpolicies and roles</span><span>, which are assigned to developers, research coordinators, andusers.</span></li>
          <li><span>Security compliance is ensured by adhering to industry standards, includingthe </span><span className="font-bold">OWASP Top 10</span><span>.</span></li>
        </ul>
        <h4 className="mt-12"><span>4. Retention Policy</span></h4>
        <p><span>Data is retained and used according to the guidelines approved by the relevantIRB. Users can request deletion of their accounts at any time.De-identified data will be retained by the research institutions of the relevant IRBs.</span></p>
        <h4 className="mt-12"><span>5. Data Sharing with Researchers</span></h4>
        <p><span>Data will be shared only with researchers who are approved by the relevant IRB. Allshared data will be fully de-identified and stored in an anonymized manner that cannot be linked to theuser.</span></p>
        <h4 className="mt-12"><span>6. Cookies or Tracking Technologies</span></h4>
        <p><span>The application uses </span><span className="font-bold">HTTP Only, secure cookies</span><span>&nbsp;forsecurely transferring access tokens granted by </span><span className="font-bold">Amazon Cognito</span><span>&nbsp;andfor managing </span><span className="font-bold">Cross-Site Request Forgery (CSRF) tokens</span><span>. Noadditional tracking technologies are used.</span></p>
        <h4 className="mt-12"><span>7. Children&rsquo;s Data</span></h4>
        <p><span>No data from children under 18 will be collected or used.</span></p>
        <h4 className="mt-12"><span>8. Third-Party Services and Data Transfer</span></h4>
        <p><span>Data will only be transferred to third parties when necessary for research approved by arelevant IRB. Transfers will strictly adhere to </span><span className="font-bold">HIPAA guidelines</span><span>&nbsp;and any additional requirements set by the relevant IRB.</span></p>
        <h4 className="mt-12"><span>9. Contact Information</span></h4>
        <p><span>If you have any questions about this privacy policy, your rights as a user, or how your data ishandled, you may contact us at:<br /></span><span className="font-bold">Email</span><span>:mhealth@pennmedicine.upenn.edu</span></p>
        <p><span></span></p>
        <h4 className="mt-12"><span>10. Updates to the Policy</span></h4>
        <p><span>This privacy policy is subject to change to ensure compliance with regulatory updatesand best practices. Any updates will be communicated to users via the Ditti Research Dashboard and posted onthis page. Users are encouraged to review this policy periodically.</span></p>
        <p><span className="font-bold">Effective Date:</span><span>&nbsp;November 25, 2024<br /></span><span className="font-bold">LastUpdated:</span><span>&nbsp;November 25, 2024</span></p>
      </div>
    </div>
  );
}
