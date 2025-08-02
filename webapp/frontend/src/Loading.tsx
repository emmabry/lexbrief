import DocIcon from './assets/doc.svg?react';
import BrainIcon from './assets/brain.svg?react';

type LoadingProps = {
    dataLoading: boolean;
    sumLoading: boolean;
  };

function Loading({ dataLoading, sumLoading }: LoadingProps) {
    console.log(`Loading component rendered with dataLoading: ${dataLoading}, sumLoading: ${sumLoading}`);
    return (
        <div className="main-card px-4 pt-5 my-5 text-center mx-auto d-flex flex-column align-items-center w-75">
            <div className="loading-card shadow p-5 pb-3 rounded-3 text-center w-50">
            <div className="spinner-border load-spin" role="status">
                    <span className="sr-only"></span>
                </div>
                <h3 className="loading-title p-2">Analysing Document</h3>
                <p className="celex-text">Please wait while we process your policy document</p>
                <div className="list-group mt-3">
                        <li className={`${dataLoading ? 'my-active' : 'inactive'} list-group-item rounded mb-2 d-flex align-items-center`}>
                            <div className={`${dataLoading ? 'loading-icon-container-active' : 'loading-icon-container-inactive'}`}>
                        <DocIcon className={`${dataLoading ? 'loading-icon-active' : 'loading-icon-inactive'}`}/>
                        </div>
                            Retrieving CELEX info</li>
                        <li className={`${sumLoading ? 'my-active' : 'inactive'} list-group-item border rounded mb-2 d-flex align-items-center`}>
                        <div className={`${sumLoading ? 'loading-icon-container-active' : 'loading-icon-container-inactive'}`}>
                        <BrainIcon className={`${sumLoading ? 'loading-icon-active' : 'loading-icon-inactive'}`}/>
                        </div>
                            Generating AI summary</li>
                </div>
                <p className="small celex-text pt-5">This usually takes 30-60 seconds. Thank you for your patience.</p>
            </div>
    </div>
    )
}

export default Loading;